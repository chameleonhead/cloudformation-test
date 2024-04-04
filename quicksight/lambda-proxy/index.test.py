import unittest
from unittest.mock import patch
from moto import mock_aws
import os

os.environ["BUCKET_NAME"] = "test-bucket"
os.environ["IDP_ISSUER"] = "https://example.com"
os.environ["APP_CLIENT_ID"] = "myclientid"
import index
from index import lambda_handler


class TestLambdaFunction(unittest.TestCase):
    @mock_aws
    def test_redirect_to_login(self):
        """リクエストにトークンが含まれていない場合に、ログインページへリダイレクトすることをテストする"""
        event = {
            "requestContext": {
                "domainName": "example.com",
                "http": {"path": "/testpath"},
            },
            "rawPath": "/testpath",
            "cookies": [],
        }
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 302)
        self.assertIn("Location", response["headers"])
        self.assertTrue(response["headers"]["Location"].startswith("/auth/login"))

    @mock_aws
    def test_s3_object_retrieval(self):
        """S3からオブジェクトを正常に取得できるかテストする"""
        # S3モックの設定
        s3 = index.boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        s3.put_object(
            Bucket="test-bucket", Key="public/index.html", Body="Hello, world!"
        )

        # 環境変数のモック
        event = {
            "requestContext": {"domainName": "example.com", "http": {"path": "/"}},
            "rawPath": "/",
            "cookies": ["tokens=somevalidtoken;"],
        }
        # トークン検証をモックに置き換え
        with patch("index.get_tokens", return_value={"id_token": "valid"}):
            response = lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "Hello, world!")

    def test_get_tokens_missing(self):
        """トークンがcookiesにない場合にNoneを返すことをテストする"""
        event = {"cookies": []}
        tokens = index.get_tokens(event)
        self.assertIsNone(tokens)

    @mock_aws
    def test_s3_object_not_found(self):
        """S3オブジェクトが見つからない場合に404レスポンスを返すことをテストする"""
        s3 = index.boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")

        event = {
            "requestContext": {"domainName": "example.com", "http": {"path": "/"}},
            "rawPath": "/non-existent",
            "cookies": ["tokens=somevalidtoken;"],
        }
        with patch("index.get_tokens", return_value={"id_token": "valid"}):
            response = lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Not Found", response["body"])

    def test_token_validation_failure(self):
        """トークン検証が失敗した場合の処理をテストする"""
        event = {
            "requestContext": {"domainName": "example.com", "http": {"path": "/"}},
            "rawPath": "/",
            "cookies": ["tokens=someinvalidtoken;"],
        }
        # トークン検証をシミュレートするモック
        with patch("index.get_tokens", return_value=None):
            response = lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 302)
        self.assertTrue(response["headers"]["Location"].startswith("/auth/login"))


if __name__ == "__main__":
    unittest.main()
