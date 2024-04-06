import boto3
import json
import os

ACCOUNT_ID = os.environ["ACCOUNT_ID"]
QUICKSIGHT_NAMESPACE = os.environ["QUICKSIGHT_NAMESPACE"]


def lambda_handler(event, context):
    # Cognitoユーザー情報の取得（ここでは例としてEメールを使用）
    user_name = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    email = event["requestContext"]["authorizer"]["jwt"]["claims"]["username"]

    # QuickSightクライアントの作成
    quicksight_client = boto3.client("quicksight")
    account_id = ACCOUNT_ID
    namespace = QUICKSIGHT_NAMESPACE

    # QuickSightにユーザーが存在するかどうかを確認
    try:
        user = quicksight_client.describe_user(
            AwsAccountId=account_id,
            Namespace=namespace,
            UserName=user_name,
        )
        print(user)
    except Exception as e:
        user = None

    # ユーザーが存在しない場合は新規作成
    if not user:
        quicksight_client.register_user(
            AwsAccountId=account_id,
            Namespace=namespace,
            IdentityType="IAM",
            Email=email,
            UserRole="READER",
            UserName=user_name,
        )

    # QuickSightの埋め込みURLを取得
    response = quicksight_client.get_session_embed_url(
        AwsAccountId=account_id,
        EntryPoint="/start",
        SessionLifetimeInMinutes=15,
        UserArn=f"arn:aws:quicksight:{account_id}:user/{namespace}/{user_name}",
    )

    # 埋め込みURLをレスポンスとして返却
    return {"statusCode": 200, "body": json.dumps({"embedUrl": response["EmbedUrl"]})}
