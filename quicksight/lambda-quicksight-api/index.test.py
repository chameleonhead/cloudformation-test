import botocore.exceptions
import unittest
from unittest.mock import MagicMock, patch
import os

os.environ["IDP_URL"] = "https://idp.example.com"
os.environ["ACCOUNT_ID"] = "YOUR_ACCOUNT_ID"
os.environ["QUICKSIGHT_NAMESPACE"] = "default"
os.environ["QUICKSIGHT_USER_ROLE"] = "QUICKSIGHT_USER_ROLE"
from index import lambda_handler


class TestLambdaFunction(unittest.TestCase):

    @patch("boto3.client")
    def test_lambda_handler_user_exists(self, mock_quicksight_client):
        # モックの設定
        mock_client_instance = MagicMock()
        mock_quicksight_client.return_value = mock_client_instance

        # モックの応答設定
        mock_client_instance.describe_user.return_value = {"User": {"Arn": "USER_ARN"}}
        mock_client_instance.generate_embed_url_for_registered_user.return_value = {
            "EmbedUrl": "YOUR_EMBED_URL"
        }

        # イベントの準備
        event = {
            "headers": {
                "referer": "https://DOMAIN_NAME",
                "host": "HOST_NAME",
            },
            "requestContext": {
                "authorizer": {
                    "jwt": {
                        "claims": {"sub": "USER_ID", "username": "test@example.com"}
                    }
                },
            },
        }

        # ハンドラの呼び出し
        response = lambda_handler(event, None)

        # 応答の検証
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], '{"embedUrl": "YOUR_EMBED_URL"}')

        # QuickSightクライアントが適切に呼び出されたかを確認
        mock_quicksight_client.assert_called_once()
        mock_client_instance.describe_user.assert_called_once_with(
            AwsAccountId="YOUR_ACCOUNT_ID",
            Namespace="default",
            UserName="QUICKSIGHT_USER_ROLE/USER_ID",
        )
        mock_client_instance.generate_embed_url_for_registered_user.assert_called_once_with(
            AwsAccountId="YOUR_ACCOUNT_ID",
            SessionLifetimeInMinutes=15,
            UserArn="USER_ARN",
            ExperienceConfiguration={
                "QuickSightConsole": {
                    "InitialPath": "/start",
                    "FeatureConfigurations": {"StatePersistence": {"Enabled": True}},
                },
            },
            AllowedDomains=["https://DOMAIN_NAME"],
        )

    @patch("requests.get")
    @patch("boto3.client")
    def test_lambda_handler_user_does_not_exist(
        self, mock_quicksight_client, mock_requests_get
    ):
        # モックの設定
        mock_client_instance = MagicMock()
        mock_quicksight_client.return_value = mock_client_instance
        mock_get_response = MagicMock()
        mock_requests_get.return_value = mock_get_response

        # モックの応答設定（ユーザーが存在しない状態）
        mock_client_instance.describe_user.side_effect = (
            botocore.exceptions.ClientError(
                {"Error": {"Code": "404", "Message": "404 Message"}}, "DescribeUser"
            )
        )
        mock_get_response.json.return_value = {"email": "test@example.com"}
        mock_client_instance.register_user.return_value = {"User": {"Arn": "USER_ARN"}}
        mock_client_instance.generate_embed_url_for_registered_user.return_value = {
            "EmbedUrl": "YOUR_EMBED_URL"
        }

        # イベントの準備
        event = {
            "headers": {
                "authorization": "AUTHORIZATION_HEADER",
                "referer": "https://DOMAIN_NAME/path",
                "host": "HOST_NAME",
            },
            "requestContext": {
                "authorizer": {"jwt": {"claims": {"sub": "USER_ID"}}},
            },
        }

        # ハンドラの呼び出し
        response = lambda_handler(event, None)

        # 応答の検証
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], '{"embedUrl": "YOUR_EMBED_URL"}')

        # QuickSightクライアントが適切に呼び出されたかを確認
        mock_quicksight_client.assert_called_once()
        mock_client_instance.describe_user.assert_called_once_with(
            AwsAccountId="YOUR_ACCOUNT_ID",
            Namespace="default",
            UserName="QUICKSIGHT_USER_ROLE/USER_ID",
        )
        mock_requests_get.assert_called_once_with(
            "https://idp.example.com/oauth2/userInfo",
            headers={"Authorization": "AUTHORIZATION_HEADER"},
        )
        mock_client_instance.register_user.assert_called_once_with(
            AwsAccountId="YOUR_ACCOUNT_ID",
            Namespace="default",
            IdentityType="IAM",
            IamArn="arn:aws:iam::YOUR_ACCOUNT_ID:role/QUICKSIGHT_USER_ROLE",
            SessionName="USER_ID",
            UserRole="READER",
            Email="test@example.com",
        )
        mock_client_instance.generate_embed_url_for_registered_user.assert_called_once_with(
            AwsAccountId="YOUR_ACCOUNT_ID",
            SessionLifetimeInMinutes=15,
            UserArn="USER_ARN",
            ExperienceConfiguration={
                "QuickSightConsole": {
                    "InitialPath": "/start",
                    "FeatureConfigurations": {"StatePersistence": {"Enabled": True}},
                },
            },
            AllowedDomains=["https://DOMAIN_NAME"],
        )


if __name__ == "__main__":
    unittest.main()
