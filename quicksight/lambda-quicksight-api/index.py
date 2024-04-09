import sys
import boto3
import botocore.exceptions
import json
import os
import urllib.parse

sys.path.append("./python")
import requests

IDP_URL = os.environ["IDP_URL"]
ACCOUNT_ID = os.environ["ACCOUNT_ID"]
QUICKSIGHT_NAMESPACE = os.environ["QUICKSIGHT_NAMESPACE"]
QUICKSIGHT_USER_ROLE = os.environ["QUICKSIGHT_USER_ROLE"]


def lambda_handler(event, context):
    # Cognitoユーザー情報の取得（ここでは例としてEメールを使用）
    sub = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    headers = event.get("headers", {})
    referer = headers.get("referer")
    if referer:
        url = urllib.parse.urlparse(referer)
        host = urllib.parse.urlunsplit((url.scheme, url.netloc, "", "", ""))
    else:
        host = headers.get("referer", f"https://{headers.get('host')}")

    # QuickSightクライアントの作成
    quicksight_client = boto3.client("quicksight")
    account_id = ACCOUNT_ID
    namespace = QUICKSIGHT_NAMESPACE
    user_role = QUICKSIGHT_USER_ROLE

    # QuickSightにユーザーが存在するかどうかを確認
    try:
        user = quicksight_client.describe_user(
            AwsAccountId=account_id,
            Namespace=namespace,
            UserName=f"{user_role}/{sub}",
        )
        user_arn = user.get("User", {}).get("Arn")
    except botocore.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ["404", "ResourceNotFoundException"]:
            user = None
        else:
            raise e

    # ユーザーが存在しない場合は新規作成
    if not user:
        authorization = event["headers"]["authorization"]
        headers = {
            "Authorization": authorization,
        }
        response = requests.get(
            f"{IDP_URL}/oauth2/userInfo",
            headers=headers,
        )
        data = response.json()
        email = data["email"]
        user = quicksight_client.register_user(
            AwsAccountId=account_id,
            Namespace=namespace,
            IdentityType="IAM",
            IamArn=f"arn:aws:iam::{account_id}:role/{user_role}",
            SessionName=sub,
            UserRole="READER",
            Email=email,
        )
        user_arn = user.get("User", {}).get("Arn")

    # QuickSightの埋め込みURLを取得
    response = quicksight_client.generate_embed_url_for_registered_user(
        AwsAccountId=account_id,
        SessionLifetimeInMinutes=15,
        UserArn=user_arn,
        ExperienceConfiguration={
            "QuickSightConsole": {
                "InitialPath": "/start",
                "FeatureConfigurations": {"StatePersistence": {"Enabled": True}},
            },
        },
        AllowedDomains=[host],
    )

    # 埋め込みURLをレスポンスとして返却
    return {"statusCode": 200, "body": json.dumps({"embedUrl": response["EmbedUrl"]})}
