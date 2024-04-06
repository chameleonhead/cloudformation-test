import unittest
from unittest.mock import MagicMock, patch
import os

os.environ["ACCOUNT_ID"] = "YOUR_ACCOUNT_ID"
os.environ["QUICKSIGHT_NAMESPACE"] = "default"
from index import lambda_handler


class TestLambdaFunction(unittest.TestCase):

    @patch("boto3.client")
    def test_lambda_handler_user_exists(self, mock_quicksight_client):
        # モックの設定
        mock_client_instance = MagicMock()
        mock_quicksight_client.return_value = mock_client_instance

        # モックの応答設定
        mock_client_instance.list_users.return_value = {
            "UserList": [{"EmailAddress": "test@example.com"}]
        }
        mock_client_instance.get_session_embed_url.return_value = {
            "EmbedUrl": "YOUR_EMBED_URL"
        }

        # イベントの準備
        event = {
            "requestContext": {
                "authorizer": {
                    "jwt": {
                        "claims": {"sub": "USER_ID", "username": "test@example.com"}
                    }
                }
            }
        }

        # ハンドラの呼び出し
        response = lambda_handler(event, None)

        # 応答の検証
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], '{"embedUrl": "YOUR_EMBED_URL"}')

        # QuickSightクライアントが適切に呼び出されたかを確認
        mock_quicksight_client.assert_called_once()
        mock_client_instance.list_users.assert_called_once_with(
            AwsAccountId="YOUR_ACCOUNT_ID", Namespace="default"
        )
        mock_client_instance.get_session_embed_url.assert_called_once_with(
            AwsAccountId="YOUR_ACCOUNT_ID",
            EntryPoint="/start",
            SessionLifetimeInMinutes=15,
            UserArn="arn:aws:quicksight:YOUR_ACCOUNT_ID:user/default/USER_ID",
        )

    @patch("boto3.client")
    def test_lambda_handler_user_does_not_exist(self, mock_quicksight_client):
        # モックの設定
        mock_client_instance = MagicMock()
        mock_quicksight_client.return_value = mock_client_instance

        # モックの応答設定（ユーザーが存在しない状態）
        mock_client_instance.list_users.return_value = {"UserList": []}
        mock_client_instance.get_session_embed_url.return_value = {
            "EmbedUrl": "YOUR_EMBED_URL"
        }

        # イベントの準備
        event = {
            "requestContext": {
                "authorizer": {
                    "jwt": {
                        "claims": {"sub": "USER_ID", "username": "test@example.com"}
                    }
                }
            }
        }

        # ハンドラの呼び出し
        response = lambda_handler(event, None)

        # 応答の検証
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], '{"embedUrl": "YOUR_EMBED_URL"}')

        # QuickSightクライアントが適切に呼び出されたかを確認
        mock_quicksight_client.assert_called_once()
        mock_client_instance.list_users.assert_called_once_with(
            AwsAccountId="YOUR_ACCOUNT_ID", Namespace="default"
        )
        mock_client_instance.register_user.assert_called_once_with(
            AwsAccountId="YOUR_ACCOUNT_ID",
            Namespace="default",
            IdentityType="IAM",
            Email="test@example.com",
            UserRole="READER",
            UserName="USER_ID",
        )
        mock_client_instance.get_session_embed_url.assert_called_once_with(
            AwsAccountId="YOUR_ACCOUNT_ID",
            EntryPoint="/start",
            SessionLifetimeInMinutes=15,
            UserArn="arn:aws:quicksight:YOUR_ACCOUNT_ID:user/default/USER_ID",
        )


if __name__ == "__main__":
    unittest.main()
