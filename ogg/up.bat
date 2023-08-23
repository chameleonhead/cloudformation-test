aws cloudformation create-stack --stack-name intra-vpc --template-body file://intra-vpc.yml
aws cloudformation wait stack-create-complete --stack-name intra-vpc
aws cloudformation create-stack --stack-name intra-resources --template-body file://intra-resources.yml --capabilities CAPABILITY_IAM
aws cloudformation wait stack-create-complete --stack-name intra-resources
aws cloudformation create-stack --stack-name multicidr-vpc --template-body file://multicidr-vpc.yml
aws cloudformation wait stack-create-complete --stack-name multicidr-vpc
aws cloudformation create-stack --stack-name multicidr-intra-connection --template-body file://multicidr-intra-connection.yml
aws cloudformation wait stack-create-complete --stack-name multicidr-intra-connection
aws cloudformation create-stack --stack-name multicidr-resources --template-body file://multicidr-resources.yml
aws cloudformation wait stack-create-complete --stack-name multicidr-resources
