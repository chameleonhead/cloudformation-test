aws cloudformation delete-stack --stack-name vpc-multiple-cidr-resources
aws cloudformation wait stack-delete-complete --stack-name vpc-multiple-cidr-resources
aws cloudformation delete-stack --stack-name vpc-multiple-cidr-intra-connection
aws cloudformation wait stack-delete-complete --stack-name vpc-multiple-cidr-intra-connection
aws cloudformation delete-stack --stack-name vpc-multiple-cidr
aws cloudformation wait stack-delete-complete --stack-name vpc-multiple-cidr
aws cloudformation delete-stack --stack-name vpc-intra-resources
aws cloudformation wait stack-delete-complete --stack-name vpc-intra-resources
aws cloudformation delete-stack --stack-name vpc-intra
aws cloudformation wait stack-delete-complete --stack-name vpc-intra
