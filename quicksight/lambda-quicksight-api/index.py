import boto3
import json
import os

ACCOUNT_ID = os.environ["ACCOUNT_ID"]
QUICKSIGHT_NAMESPACE = os.environ["QUICKSIGHT_NAMESPACE"]
QUICKSIGHT_USER_ROLE_NAME = os.environ["QUICKSIGHT_USER_ROLE_NAME"]


def lambda_handler(event, context):
    # Cognitoユーザー情報の取得（ここでは例としてEメールを使用）
    email = event["requestContext"]["authorizer"]["claims"]["email"]
    print(event)

    # QuickSightクライアントの作成
    quicksight_client = boto3.client("quicksight")
    account_id = ACCOUNT_ID
    namespace = QUICKSIGHT_NAMESPACE
    quicksight_role_name = QUICKSIGHT_USER_ROLE_NAME

    # QuickSightにユーザーが存在するかどうかを確認
    users = quicksight_client.list_users(AwsAccountId=account_id, Namespace=namespace)
    user_exists = any(
        user for user in users["UserList"] if user["EmailAddress"] == email
    )

    # ユーザーが存在しない場合は新規作成
    if not user_exists:
        quicksight_client.register_user(
            AwsAccountId=account_id,
            Namespace=namespace,
            IdentityType="IAM",
            Email=email,
            UserRole="READER",
            IamArn=f"arn:aws:iam::{account_id}:role/{quicksight_role_name}",
            SessionName=email,  # QuickSightのユーザー名やEメールなど、一意のセッション名を設定
        )

    # QuickSightの埋め込みURLを取得
    response = quicksight_client.get_session_embed_url(
        AwsAccountId=account_id,
        EntryPoint="/start",
        SessionLifetimeInMinutes=15,
        UserArn=f"arn:aws:quicksight:{account_id}:user/{namespace}/{email}",
    )

    # 埋め込みURLをレスポンスとして返却
    return {"statusCode": 200, "body": json.dumps({"embedUrl": response["EmbedUrl"]})}
