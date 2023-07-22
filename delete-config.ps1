$LIVERUN=$true
aws ec2 describe-regions --region us-east-1 --query "Regions[].[RegionName]" --output text | %{
  recorder=$(aws configservice describe-configuration-recorders --region $_ --query "ConfigurationRecorders[].name" --output text)
  echo "$_ $recorder"
  if ($recorder -and $LIVERUN) {
    aws --region $_ configservice delete-configuration-recorder --configuration-recorder-name $recorder
  }
  channel=$(aws configservice describe-delivery-channels --region $_ --query "DeliveryChannels[].name" --output text)
  echo "$_ $channel"
  if ($channel -and $LIVERUN) {
    aws --region $_ configservice delete-delivery-channel --delivery-channel-name $channel
  }
}
