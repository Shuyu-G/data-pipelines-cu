variable "bucket_name" {
  description = "Unique name for the S3 bucket"
  type        = string
}

variable "force_destroy" {
  description = "Whether Terraform may delete non-empty buckets"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to the bucket resources"
  type        = map(string)
  default     = {}
}
