output "bucket_names" {
  description = "S3 bucket names by pipeline stage"
  value       = { for stage, bucket in module.storage_bucket : stage => bucket.bucket_name }
}

output "bucket_arns" {
  description = "S3 bucket ARNs by pipeline stage"
  value       = { for stage, bucket in module.storage_bucket : stage => bucket.bucket_arn }
}

output "dynamodb_table_name" {
  description = "DynamoDB table name used for pipeline metadata"
  value       = aws_dynamodb_table.pipeline_metadata.name
}

output "dynamodb_table_arn" {
  description = "DynamoDB table ARN used for pipeline metadata"
  value       = aws_dynamodb_table.pipeline_metadata.arn
}

output "aws_region" {
  description = "AWS region where the baseline infrastructure is deployed"
  value       = var.aws_region
}
