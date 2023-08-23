aws cloudformation create-stack --stack-name intra-vpc --template-body file://intra-vpc.yml
aws cloudformation create-stack --stack-name multicidr-vpc --template-body file://multicidr-vpc.yml
aws cloudformation wait stack-create-complete --stack-name intra-vpc
aws cloudformation wait stack-create-complete --stack-name multicidr-vpc

aws cloudformation create-stack --stack-name tgw --template-body file://tgw.yml
aws cloudformation wait stack-create-complete --stack-name tgw

aws cloudformation create-stack --stack-name intra-resources --template-body file://intra-resources.yml --capabilities CAPABILITY_IAM
aws cloudformation create-stack --stack-name multicidr-resources --template-body file://multicidr-resources.yml
aws cloudformation wait stack-create-complete --stack-name intra-resources
aws cloudformation wait stack-create-complete --stack-name multicidr-resources
