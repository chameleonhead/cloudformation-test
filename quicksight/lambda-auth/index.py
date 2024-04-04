import sys

sys.path.append("./python")
import json
import os
from jose import jwt, jwk, ExpiredSignatureError, JWTError
import requests
import urllib.parse
import http.cookies

IDP_ISSUER = os.environ["IDP_ISSUER"]
IDP_ISSUER_KEYS_URL = f"{IDP_ISSUER}/.well-known/jwks.json"
IDP_URL = os.environ["IDP_URL"]
IDP_LOGIN_PAGE = f"{IDP_URL}/login"
IDP_TOKEN_ENDPOINT = f"{IDP_URL}/oauth2/token"
APP_CLIENT_ID = os.environ["APP_CLIENT_ID"]
APP_CLIENT_SECRET = "ujab65625o64l6hu1g3uqlt1p4rvu4vu0romr36t667sb06o9mi"
APP_REDIRECT_URI = os.environ["APP_REDIRECT_URI"]


def lambda_handler(event, context):
    path = event.get("rawPath", event["requestContext"]["http"]["path"])
    # HTTP API と REST API の両方に対応
    query_string_parameters = event.get("queryStringParameters", {})
    if path == "/auth/callback":
        # Cognitoの認証コードをクエリパラメータから取得
        code = query_string_parameters.get("code")
        if not code:
            return {
                "statusCode": 400,
                "headers": set_security_headers({}),
                "body": "Bad Request",
            }

        # Cognitoにトークンを要求
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": APP_CLIENT_ID,
            "redirect_uri": APP_REDIRECT_URI,
        }

        response = requests.post(
            f"{IDP_URL}/oauth2/token",
            data=body,
            headers=headers,
            auth=(APP_CLIENT_ID, APP_CLIENT_SECRET),
        )
        if response.status_code == 200:
            # トークンの取得に成功した場合
            tokens = response.json()
            original_page = tokens.get("state")

            # トークンをクッキーに設定してリダイレクト
            headers = {
                "Location": original_page if original_page else "/",
                "Set-Cookie": f"tokens={urllib.parse.quote_plus(json.dumps(tokens))}; Secure; HttpOnly; Path=/",
            }
            return {
                "statusCode": 302,
                "headers": set_security_headers(headers),
                "body": "",
            }
        else:
            # トークンの取得に失敗した場合
            return {
                "statusCode": response.status_code,
                "headers": set_security_headers({}),
                "body": response.text,
            }
    tokens = get_tokens(event)

    if path == "/auth/login":
        if tokens:
            return redirect_to(query_string_parameters.get("redirect"))
        else:
            return redirect_to_cognito(query_string_parameters.get("redirect"))
    else:
        return {
            "statusCode": 404,
            "headers": set_security_headers({}),
            "body": "Not Found",
        }


def redirect_to(redirect_url):
    return {
        "statusCode": 302,
        "headers": set_security_headers({"Location": redirect_url}),
        "body": json.dumps({"message": "Redirecting to authentication page..."}),
    }


def redirect_to_cognito(redirect_url=None):
    login_page = f"{IDP_URL}/login"
    login_page += f"?response_type=code"
    login_page += f"&client_id={APP_CLIENT_ID}"
    login_page += f"&redirect_uri={urllib.parse.quote_plus(APP_REDIRECT_URI)}"
    login_page += f"&scope=openid+profile+email"
    if redirect_url:
        login_page += f"&state={urllib.parse.quote_plus(redirect_url)}"
    return redirect_to(login_page)


def set_security_headers(headers):
    headers.update(
        {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; object-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self';",
            "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
        }
    )
    return headers


def get_tokens(event):
    cookies = event.get("cookies", [])
    tokens = None
    for cookie_str in cookies:
        c = http.cookies.SimpleCookie(cookie_str)
        tokens = c.get("tokens").value if "tokens" in c else None
        if tokens:
            tokens = json.loads(urllib.parse.unquote_plus(tokens))
            break

    if not tokens or not tokens.get("id_token"):
        return None

    id_token = tokens.get("id_token")
    # JWKSから公開鍵を取得
    keys = requests.get(IDP_ISSUER_KEYS_URL).json()["keys"]
    headers = jwt.get_unverified_headers(id_token)
    print(jwt.get_unverified_claims(id_token))
    kid = headers["kid"]

    # kidにマッチする公開鍵を探す
    key = next((key for key in keys if key["kid"] == kid), None)
    if key is None:
        return {
            "statusCode": 401,
            "body": json.dumps({"message": "Public key not found"}),
        }

    try:
        # 公開鍵を使用してトークンを検証
        public_key = jwk.construct(key)
        jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=APP_CLIENT_ID,
            issuer=IDP_ISSUER,
            access_token=tokens.get("access_token"),
        )
        return tokens
    except ExpiredSignatureError:
        print(e)
        # 有効期限エラー
        return None
    except JWTError as e:
        print(e)
        # その他のJWTエラー（署名検証エラーなど）
        return None
