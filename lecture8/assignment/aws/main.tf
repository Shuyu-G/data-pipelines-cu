terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

locals {
  project_slug = lower(replace(var.project_name, "_", "-"))
  bucket_prefix = lower(
    "${local.project_slug}-${var.environment}-${data.aws_caller_identity.current.account_id}"
  )

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Course      = "Lecture8"
  }
}

module "storage_bucket" {
  for_each = toset(var.bucket_suffixes)

  source = "./modules/s3-bucket"

  bucket_name   = "${local.bucket_prefix}-${each.key}"
  force_destroy = var.force_destroy_buckets
  tags = merge(
    local.common_tags,
    {
      Stage = each.key
    }
  )
}

resource "aws_dynamodb_table" "pipeline_metadata" {
  name         = "${local.project_slug}-${var.environment}-pipeline-metadata"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pipeline_id"
  range_key    = "run_id"

  attribute {
    name = "pipeline_id"
    type = "S"
  }

  attribute {
    name = "run_id"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = merge(
    local.common_tags,
    {
      Resource = "pipeline-metadata"
    }
  )
}
