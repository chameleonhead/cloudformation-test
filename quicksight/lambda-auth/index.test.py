import unittest
from unittest.mock import patch, MagicMock
import os

os.environ["IDP_ISSUER"] = "https://example.com"
os.environ["IDP_URL"] = "https://idp.example.com"
os.environ["APP_CLIENT_ID"] = "myclientid"
os.environ["APP_CLIENT_SECRET"] = "myclientsecret"
os.environ["APP_REDIRECT_URI"] = "https://myapp.com/callback"

from index import lambda_handler


class TestLambdaFunction(unittest.TestCase):
    @patch("requests.post")
    def test_auth_callback_with_no_code(self, mock_post):
        """認証コードがない場合、400 Bad Requestを返すことをテストする"""
        event = {
            "rawPath": "/auth/callback",
            "queryStringParameters": {},
        }
        response = lambda_handler(event, {})
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("Bad Request", response["body"])

    @patch("requests.post")
    def test_auth_callback_token_failure(self, mock_post):
        """トークン取得に失敗した場合、IDプロバイダからのエラーレスポンスを返すことをテストする"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Error"
        mock_post.return_value = mock_response

        event = {
            "rawPath": "/auth/callback",
            "queryStringParameters": {"code": "invalid_code"},
        }
        response = lambda_handler(event, {})
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("Error", response["body"])

    @patch("requests.post")
    def test_auth_callback_token_success(self, mock_post):
        """トークン取得に成功した場合、クッキーにトークンを設定し、指定されたURLにリダイレクトする"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "access_token_value",
            "id_token": "id_token_value",
            "refresh_token": "refresh_token_value",
            "state": "https://original-page.com",
        }
        mock_post.return_value = mock_response

        event = {
            "rawPath": "/auth/callback",
            "queryStringParameters": {"code": "valid_code"},
        }
        response = lambda_handler(event, {})
        self.assertEqual(response["statusCode"], 302)
        self.assertTrue("Location" in response["headers"])
        self.assertTrue("Set-Cookie" in response["headers"])
        self.assertIn("https://original-page.com", response["headers"]["Location"])

    def test_auth_login_redirect(self):
        """'/auth/login'へのアクセス時に、Cognitoのログインページへ正しくリダイレクトする"""
        event = {
            "rawPath": "/auth/login",
            "requestContext": {
                "domainName": "example.com",
            },
            "queryStringParameters": {"redirect": "https://redirect-page.com"},
        }
        response = lambda_handler(event, {})
        self.assertEqual(response["statusCode"], 302)
        self.assertIn("https://idp.example.com/login", response["headers"]["Location"])
        self.assertIn("response_type=code", response["headers"]["Location"])
        self.assertIn("client_id=myclientid", response["headers"]["Location"])
        self.assertIn(
            "state=https%3A%2F%2Fredirect-page.com",
            response["headers"]["Location"],
        )
        self.assertIn("scope=openid+profile+email", response["headers"]["Location"])
        self.assertIn(
            "state=https%3A%2F%2Fredirect-page.com", response["headers"]["Location"]
        )

    # トークン検証をテスト
    def test_token_without_cookie(self):
        event = {
            "rawPath": "/auth/token",
        }
        result = lambda_handler(event, None)
        self.assertEqual(result["statusCode"], 400)

    # トークンリフレッシュをテスト
    def test_refresh_without_cookie(self):
        event = {
            "rawPath": "/auth/refresh",
        }
        result = lambda_handler(event, None)
        self.assertEqual(result["statusCode"], 400)


if __name__ == "__main__":
    unittest.main()
