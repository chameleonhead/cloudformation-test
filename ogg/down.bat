aws cloudformation delete-stack --stack-name multicidr-resources
aws cloudformation delete-stack --stack-name vpc-intra-resources
aws cloudformation wait stack-delete-complete --stack-name multicidr-resources
aws cloudformation wait stack-delete-complete --stack-name vpc-intra-resources

aws cloudformation delete-stack --stack-name tgw
aws cloudformation wait stack-delete-complete --stack-name tgw

aws cloudformation delete-stack --stack-name multicidr-vpc
aws cloudformation delete-stack --stack-name vpc-intra
aws cloudformation wait stack-delete-complete --stack-name multicidr-vpc
aws cloudformation wait stack-delete-complete --stack-name vpc-intra
