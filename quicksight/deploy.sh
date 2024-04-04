#/bin/bash -e
v=2

cd lambda-proxy
pip install --platform=manylinux2014_x86_64 --implementation=cp --target=python --only-binary=:all: --upgrade python-jose requests
python index.test.py
zip -q lambda-proxy.zip index.py -r python
aws s3 cp lambda-proxy.zip s3://test-lambda-bucket-for-qs/lambda-proxy-$v.zip
cd ..

cd lambda-auth
pip install --platform=manylinux2014_x86_64 --implementation=cp --target=python --only-binary=:all: --upgrade python-jose requests
python index.test.py
zip -q lambda-auth.zip index.py -r python
aws s3 cp lambda-auth.zip s3://test-lambda-bucket-for-qs/lambda-auth-$v.zip
cd ..

aws cloudformation update-stack --stack-name quicksight-app --template-body file://quicksight-app.yml --capabilities CAPABILITY_NAMED_IAM --parameters ParameterKey=LambdaS3KeyS3Proxy,ParameterValue=lambda-proxy-$v.zip ParameterKey=LambdaS3KeyAuth,ParameterValue=lambda-auth-$v.zip

aws s3 cp --recursive public/ s3://test-spa-app-with-qs/public/

