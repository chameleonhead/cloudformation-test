import sys
import boto3
from botocore.exceptions import ClientError
import json
from datetime import datetime
import os
import urllib.parse
import http.cookies

sys.path.append("./python")
from jose import jwt, jwk, ExpiredSignatureError, JWTError
import requests

s3 = boto3.client("s3")
BUCKET_NAME = os.environ["BUCKET_NAME"]
PUBLIC_PREFIX = "public/"

IDP_ISSUER = os.environ["IDP_ISSUER"]
IDP_ISSUER_KEYS_URL = f"{IDP_ISSUER}/.well-known/jwks.json"
APP_CLIENT_ID = os.environ["APP_CLIENT_ID"]


def lambda_handler(event, context):
    tokens = get_tokens(event)
    domain_name = event["requestContext"]["domainName"]
    path = event.get("rawPath", "")
    query_string = event.get("rawQueryString")

    request_url = f"https://{domain_name}{path}"
    if query_string:
        request_url += f"?{query_string}"

    if not tokens:
        print("Redirect to login page")
        return redirect_to_login(request_url)

    path = path.lstrip("/")
    if path.endswith("/") or not path:
        path += "index.html"

    s3_object_key = f"{PUBLIC_PREFIX}{path}"
    headers = event.get("headers", {})

    print(f"S3 Key: {s3_object_key}")
    try:
        get_object_args = {}
        get_object_args["Bucket"] = BUCKET_NAME
        get_object_args["Key"] = s3_object_key
        if headers.get("If-None-Match"):
            get_object_args["IfNoneMatch"] = headers.get("If-None-Match")
        if headers.get("If-Modified-Since"):
            get_object_args["IfModifiedSince"] = datetime.strptime(
                headers.get("If-Modified-Since", ""), "%a, %d %b %Y %H:%M:%S GMT"
            )

        s3_response = s3.get_object(**get_object_args)

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ["NoSuchKey", "404"]:
            # 404の場合、index.htmlを再度試行
            s3_object_key = f"{PUBLIC_PREFIX}index.html"
            try:
                s3_response = s3.get_object(Bucket=BUCKET_NAME, Key=s3_object_key)
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code in ["NoSuchKey", "404"]:
                    # 404の場合、index.htmlを再度試行
                    return {
                        "statusCode": 404,
                        "headers": set_security_headers({}),
                        "body": "Not Found",
                    }
                elif error_code == "304":
                    # キャッシュが有効の場合
                    return {"statusCode": 304, "headers": set_security_headers({})}
                else:
                    return {"statusCode": 500, "body": "Internal Server Error"}
        elif error_code == "304":
            # キャッシュが有効の場合
            return {"statusCode": 304, "headers": set_security_headers({})}
        else:
            return {"statusCode": 500, "body": "Internal Server Error"}

    body = s3_response["Body"].read()
    response = {
        "statusCode": 200,
        "body": body.decode("utf-8"),
        "headers": set_security_headers(
            {
                "Content-Type": s3_response["ContentType"],
                "ETag": s3_response["ETag"],
                "Last-Modified": s3_response["LastModified"].strftime(
                    "%a, %d %b %Y %H:%M:%S GMT"
                ),
            }
        ),
    }

    return response


def redirect_to_login(request_url):
    login_page = f"/auth/login?redirect={urllib.parse.quote_plus(request_url)}"

    return {
        "statusCode": 302,
        "headers": set_security_headers({"Location": login_page}),
        "body": json.dumps({"message": "Redirecting to authentication page..."}),
    }


def set_security_headers(headers):
    headers.update(
        {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src *; script-src * 'unsafe-inline'; connect-src * 'unsafe-inline'; img-src * data: blob: 'unsafe-inline'; frame-src *; style-src * 'unsafe-inline';",
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
    except ExpiredSignatureError as e:
        print(e)
        # 有効期限エラー
        return None
    except JWTError as e:
        print(e)
        # その他のJWTエラー（署名検証エラーなど）
        return None
