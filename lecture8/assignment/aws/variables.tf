variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name used in resource naming"
  type        = string
  default     = "data-pipeline"
}

variable "environment" {
  description = "Environment name used in resource naming"
  type        = string
  default     = "dev"
}

variable "bucket_suffixes" {
  description = "Storage stages to create as S3 buckets"
  type        = list(string)
  default     = ["raw", "staged", "curated"]
}

variable "force_destroy_buckets" {
  description = "Whether Terraform may delete non-empty buckets during destroy"
  type        = bool
  default     = false
}
