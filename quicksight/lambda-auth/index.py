import sys
import datetime
import http.cookies
import json
import os
import urllib.parse

sys.path.append("./python")
from jose import jwt, jwk, ExpiredSignatureError, JWTError
import requests

IDP_ISSUER = os.environ["IDP_ISSUER"]
IDP_ISSUER_KEYS_URL = f"{IDP_ISSUER}/.well-known/jwks.json"
IDP_URL = os.environ["IDP_URL"]
IDP_LOGIN_PAGE = f"{IDP_URL}/login"
IDP_TOKEN_ENDPOINT = f"{IDP_URL}/oauth2/token"
APP_CLIENT_ID = os.environ["APP_CLIENT_ID"]
APP_CLIENT_SECRET = "ujab65625o64l6hu1g3uqlt1p4rvu4vu0romr36t667sb06o9mi"
APP_REDIRECT_URI = os.environ["APP_REDIRECT_URI"]


def lambda_handler(event, context):
    path = event.get("rawPath")
    if path == "/auth/callback":
        return lambda_handler_callback(event, context)

    if path == "/auth/login":
        return lambda_handler_login(event, context)
    elif path == "/auth/token":
        return lambda_handler_token(event, context)
    elif path == "/auth/refresh":
        return lambda_handler_refresh(event, context)
    else:
        return {
            "statusCode": 404,
            "headers": set_security_headers({}),
            "body": "Not Found",
        }


def lambda_handler_callback(event, context):
    # Cognitoの認証コードをクエリパラメータから取得
    query_string_parameters = event.get("queryStringParameters", {})
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
            "Set-Cookie": tokens_to_set_cookie(tokens),
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


def lambda_handler_login(event, context):
    tokens = get_tokens_from_cookie(event)
    query_string_parameters = event.get("queryStringParameters", {})
    redirect_url = query_string_parameters.get("redirect")
    if tokens:
        result = verify_token(tokens.get("id_token"), tokens.get("access_token"))
        if "Token" in result and result["ExpiresIn"] > datetime.timedelta(minutes=20):
            return {
                "statusCode": 302,
                "headers": set_security_headers({"Location": redirect_url}),
                "body": json.dumps({"message": "Redirecting to page..."}),
            }

        if "Token" in result and tokens.get("refresh_token"):
            tokens = refresh_token(tokens.get("refresh_token"))
            if tokens:
                return {
                    "statusCode": 302,
                    "headers": set_security_headers(
                        {
                            "Set-Cookie": tokens_to_set_cookie(tokens),
                            "Location": redirect_url,
                        }
                    ),
                    "body": json.dumps({"message": "Redirecting to page..."}),
                }

    login_page = f"{IDP_URL}/login"
    login_page += f"?response_type=code"
    login_page += f"&client_id={APP_CLIENT_ID}"
    login_page += f"&redirect_uri={urllib.parse.quote_plus(APP_REDIRECT_URI)}"
    login_page += f"&scope=openid+profile+email"
    if redirect_url:
        login_page += f"&state={urllib.parse.quote_plus(redirect_url)}"

    return {
        "statusCode": 302,
        "headers": set_security_headers({"Location": login_page}),
        "body": json.dumps({"message": "Redirecting to authentication page..."}),
    }


def lambda_handler_token(event, context):
    tokens = get_tokens_from_cookie(event)
    if not tokens:
        return {
            "statusCode": 400,
            "headers": set_security_headers({}),
            "body": json.dumps({"message": "Bad Request"}),
        }

    result = verify_token(tokens.get("id_token"), tokens.get("access_token"))
    if not "Token" in result and result["ExpiresIn"] < datetime.timedelta(seconds=10):
        return {
            "statusCode": 401,
            "headers": set_security_headers({}),
            "body": json.dumps({"message": "Unauthorized"}),
        }

    return {
        "statusCode": 200,
        "headers": set_security_headers({}),
        "body": json.dumps(tokens),
    }


def lambda_handler_refresh(event, context):
    tokens = get_tokens_from_cookie(event)
    if not tokens:
        return {
            "statusCode": 400,
            "headers": set_security_headers({}),
            "body": json.dumps({"message": "Bad Request"}),
        }

    result = verify_token(tokens.get("id_token"), tokens.get("access_token"))
    if "Token" in result and result["ExpiresIn"] > datetime.timedelta(minutes=20):
        return {
            "statusCode": 304,
            "headers": set_security_headers({}),
        }

    if "Token" in result:
        new_tokens = refresh_token(tokens.get("refresh_token"))
        if new_tokens:
            headers = {
                "Set-Cookie": tokens_to_set_cookie(new_tokens),
            }
            return {
                "statusCode": 200,
                "headers": set_security_headers(headers),
                "body": json.dumps(tokens),
            }

    return {
        "statusCode": 401,
        "headers": set_security_headers({}),
        "body": json.dumps({"message": "Unauthorized"}),
    }


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


def get_tokens_from_cookie(event):
    cookies = event.get("cookies", [])
    tokens = None
    for cookie_str in cookies:
        c = http.cookies.SimpleCookie(cookie_str)
        tokens = c.get("tokens").value if "tokens" in c else None
        if tokens:
            return json.loads(urllib.parse.unquote_plus(tokens))
    return None


def tokens_to_set_cookie(tokens):
    tokens_to_store = {
        "id_token": tokens.get("id_token"),
        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
    }
    return f"tokens={urllib.parse.quote_plus(json.dumps(tokens_to_store))}; Secure; HttpOnly; Path=/"


def verify_token(token, access_token):
    # JWKSから公開鍵を取得
    keys = requests.get(IDP_ISSUER_KEYS_URL).json()["keys"]
    headers = jwt.get_unverified_headers(token)
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
        decoded_token = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=APP_CLIENT_ID,
            issuer=IDP_ISSUER,
            access_token=access_token,
        )
        return {
            "Token": decoded_token,
            "ExpiresIn": datetime.datetime.fromtimestamp(decoded_token.get("exp", 0))
            - datetime.datetime.now(),
        }
    except ExpiredSignatureError as e:
        print(e)
        # 有効期限エラー
        decoded_token = jwt.get_unverified_claims(token)
        return {
            "Token": decoded_token,
            "ExpiresIn": datetime.datetime.fromtimestamp(decoded_token.get("exp", 0))
            - datetime.datetime.now(),
        }
    except JWTError as e:
        print(e)
        # その他のJWTエラー（署名検証エラーなど）
        return {}


def refresh_token(token):
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    body = {
        "grant_type": "refresh_token",
        "refresh_token": token,
    }

    response = requests.post(
        f"{IDP_URL}/oauth2/token",
        data=body,
        headers=headers,
        auth=(APP_CLIENT_ID, APP_CLIENT_SECRET),
    )
    if response.status_code == 200:
        # トークンの取得に成功した場合
        return response.json()
    else:
        return None
