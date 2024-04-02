cd lambda-proxy
pip install --platform=manylinux2014_x86_64 --implementation=cp --target=python --only-binary=:all: --upgrade python-jose requests
zip lambda-proxy.zip index.py -r python
aws s3 cp lambda-proxy.zip s3://test-lambda-bucket-for-qs/lambda-proxy-5.zip
cd ..

aws cloudformation update-stack --stack-name quicksight-app --template-body file://quicksight-app.yml --capabilities CAPABILITY_NAMED_IAM --parameters ParameterKey=LambdaS3Key,ParameterValue=lambda-proxy-5.zip

aws s3 cp --recursive public/ s3://test-spa-app-with-qs/public/

