import sys

sys.path.append("./python")
import boto3
import json
import os
from jose import jwt, jwk
import requests
import urllib.parse
import http.cookies

s3 = boto3.client("s3")
BUCKET_NAME = os.environ["BUCKET_NAME"]
PUBLIC_PREFIX = "public/"

IDP_ISSUER = os.environ["IDP_ISSUER"]
IDP_AUDIENCE = os.environ["IDP_AUDIENCE"]
IDP_ISSUER_KEYS_URL = f"{IDP_ISSUER}/.well-known/jwks.json"
IDP_URL = os.environ["IDP_URL"]
IDP_LOGIN_PAGE = f"{IDP_URL}/login"
IDP_TOKEN_ENDPOINT = f"{IDP_URL}/oauth2/token"
APP_CLIENT_ID = os.environ["APP_CLIENT_ID"]
APP_CLIENT_SECRET = "ujab65625o64l6hu1g3uqlt1p4rvu4vu0romr36t667sb06o9mi"
APP_REDIRECT_URI = os.environ["APP_REDIRECT_URI"]


def lambda_handler(event, context):
    cookies_str = event.get("headers", {}).get("Cookie", "")
    cookies = http.cookies.SimpleCookie(cookies_str)
    token = cookies.get("id_token").value if "id_token" in cookies else None
    domain_name = event["requestContext"]["domainName"]
    path = event.get(
        "rawPath", event["requestContext"]["http"]["path"]
    )  # HTTP API と REST API の両方に対応
    query_string_parameters = event.get("queryStringParameters", {})

    token_is_valid = False
    if token:
        # JWKSから公開鍵を取得
        keys = requests.get(IDP_ISSUER_KEYS_URL).json()["keys"]
        headers = jwt.get_unverified_headers(token)
        kid = headers["kid"]

        # kidにマッチする公開鍵を探す
        key = next((key for key in keys if key["kid"] == kid), None)
        if key:
            try:
                # 公開鍵を使用してトークンを検証
                public_key = jwk.construct(key)
                jwt.decode(
                    token,
                    public_key,
                    algorithms=["RS256"],
                    issuer=IDP_ISSUER,
                    audience=IDP_AUDIENCE,
                )
                token_is_valid = True
            except:
                pass

    if path == "/auth/login":
        if token_is_valid:
            return redirect_to(query_string_parameters.get("redirect"))
        else:
            return redirect_to_cognito()
    elif path == "/auth/callback":
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
            id_token = tokens["id_token"]
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]
            original_page = tokens.get("state")

            # トークンをクッキーに設定してリダイレクト
            headers = {
                "Location": original_page if original_page else "/",
            }
            multiValueHeaders = {
                "Set-Cookie": [
                    f"id_token={id_token}; Secure; HttpOnly; Path=/",
                    f"access_token={access_token}; Secure; HttpOnly; Path=/",
                    f"refresh_token={refresh_token}; Secure; HttpOnly; Path=/",
                ],
            }
            return {
                "statusCode": 302,
                "headers": set_security_headers(headers),
                "multiValueHeaders": multiValueHeaders,
                "body": "",
            }
        else:
            # トークンの取得に失敗した場合
            return {
                "statusCode": response.status_code,
                headers: set_security_headers({}),
                "body": response.text,
            }
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


def redirect_to_cognito():
    login_page = f"{IDP_URL}/login"
    login_page += f"?response_type=code"
    login_page += f"&client_id={APP_CLIENT_ID}"
    login_page += f"&redirect_uri={urllib.parse.quote(APP_REDIRECT_URI)}"
    login_page += f"&scope=openid+profile+email"
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
