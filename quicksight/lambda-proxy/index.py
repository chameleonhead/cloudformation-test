import boto3
from datetime import datetime
from botocore.exceptions import ClientError
import os

s3 = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']
PUBLIC_PREFIX = 'public/'

def lambda_handler(event, context):
    path = event['rawPath'].lstrip('/')
    if path.endswith('/') or not path:
        path += 'index.html'

    s3_object_key = f"{PUBLIC_PREFIX}{path}"
    headers = event.get('headers', {})

    try:
        get_object_args = {}
        get_object_args['Bucket'] = BUCKET_NAME
        get_object_args['Key'] = s3_object_key
        if headers.get('If-None-Match'):
            get_object_args['IfNoneMatch'] = headers.get('If-None-Match')
        if headers.get('If-Modified-Since'):
            get_object_args['IfModifiedSince'] = datetime.strptime(headers.get('If-Modified-Since', ''), '%a, %d %b %Y %H:%M:%S GMT')
            
        s3_response = s3.get_object(**get_object_args)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code in ['NoSuchKey', '404']:
            # 404の場合、index.htmlを再度試行
            s3_object_key = f"{PUBLIC_PREFIX}index.html"
            try:
                s3_response = s3.get_object(Bucket=BUCKET_NAME, Key=s3_object_key)
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code in ['NoSuchKey', '404']:
                    # 404の場合、index.htmlを再度試行
                    return {'statusCode': 404, 'headers': set_security_headers({}), 'body': 'Not Found'}
                elif error_code == '304':
                    # キャッシュが有効の場合
                    return {'statusCode': 304, 'headers': set_security_headers({})}
                else:
                    return {'statusCode': 500, 'body': 'Internal Server Error'}
        elif error_code == '304':
            # キャッシュが有効の場合
            return {'statusCode': 304, 'headers': set_security_headers({})}
        else:
            return {'statusCode': 500, 'body': 'Internal Server Error'}

    body = s3_response['Body'].read()
    response = {
        'statusCode': 200,
        'body': body.decode('utf-8'),
        'headers': set_security_headers({
            'Content-Type': s3_response['ContentType'],
            'ETag': s3_response['ETag'],
            'Last-Modified': s3_response['LastModified'].strftime('%a, %d %b %Y %H:%M:%S GMT'),
        }),
    }

    return response

def set_security_headers(headers):
    headers.update({
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'Content-Security-Policy': "default-src 'self'; script-src 'self'; object-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self';",
        'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload',
    })
    return headers
