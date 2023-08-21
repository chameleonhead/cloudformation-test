aws cloudformation create-stack --stack-name vpc-intra --template-body file://vpc-intra.yml
aws cloudformation wait stack-create-complete --stack-name vpc-intra
aws cloudformation create-stack --stack-name vpc-intra-resources --template-body file://vpc-intra-resources.yml --capabilities CAPABILITY_IAM
aws cloudformation wait stack-create-complete --stack-name vpc-intra-resources
aws cloudformation create-stack --stack-name vpc-multiple-cidr --template-body file://vpc-multiple-cidr.yml
aws cloudformation wait stack-create-complete --stack-name vpc-multiple-cidr
aws cloudformation create-stack --stack-name vpc-multiple-cidr-intra-connection --template-body file://vpc-multiple-cidr-intra-connection.yml
aws cloudformation wait stack-create-complete --stack-name vpc-multiple-cidr-intra-connection
aws cloudformation create-stack --stack-name vpc-multiple-cidr-resources --template-body file://vpc-multiple-cidr-resources.yml
aws cloudformation wait stack-create-complete --stack-name vpc-multiple-cidr-resources
