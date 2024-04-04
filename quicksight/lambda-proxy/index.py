import sys

sys.path.append("./python")
import boto3
from botocore.exceptions import ClientError
import json
from datetime import datetime
import os
from jose import jwt, jwk, ExpiredSignatureError, JWTError
import requests
import urllib.parse
import http.cookies

s3 = boto3.client("s3")
BUCKET_NAME = os.environ["BUCKET_NAME"]
PUBLIC_PREFIX = "public/"

IDP_ISSUER = os.environ["IDP_ISSUER"]
IDP_AUDIENCE = os.environ["IDP_AUDIENCE"]
IDP_ISSUER_KEYS_URL = f"{IDP_ISSUER}/.well-known/jwks.json"


def lambda_handler(event, context):
    cookies = event.get("cookies", [])
    for cookie_str in cookies:
        c = http.cookies.SimpleCookie(cookie_str)
        id_token = c.get("id_token").value if "id_token" in c else None
        if id_token:
            break
    domain_name = event["requestContext"]["domainName"]
    path = event.get(
        "rawPath", event["requestContext"]["http"]["path"]
    )  # HTTP API と REST API の両方に対応
    query_string_parameters = event.get("queryStringParameters", {})
    query_string = event.get(
        "rawQueryString", urllib.parse.urlencode(query_string_parameters)
    )

    request_url = f"https://{domain_name}{path}"
    if query_string:
        request_url += f"?{query_string}"

    if not id_token:
        print("No id_token")
        return redirect_to_login(request_url)

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
            issuer=IDP_ISSUER,
            audience=IDP_AUDIENCE,
        )

    except ExpiredSignatureError:
        print(e)
        # 有効期限エラー
        return redirect_to_login(request_url)
    except JWTError as e:
        print(e)
        # その他のJWTエラー（署名検証エラーなど）
        return redirect_to_login(request_url)

    path = event["rawPath"].lstrip("/")
    if path.endswith("/") or not path:
        path += "index.html"

    s3_object_key = f"{PUBLIC_PREFIX}{path}"
    headers = event.get("headers", {})

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
    login_page = f"/auth/login?redirect={urllib.parse.quote(request_url)}"

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
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; object-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self';",
            "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
        }
    )
    return headers
