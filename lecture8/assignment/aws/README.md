# Lecture 8 Assignment (AWS): Baseline Infrastructure

This Terraform project deploys baseline AWS infrastructure for a data pipeline:

1. Three S3 buckets for pipeline stages: `raw`, `staged`, and `curated`
2. One DynamoDB table for pipeline metadata

The configuration demonstrates the required Lecture 8 concepts:

- A reusable Terraform module in `modules/s3-bucket`
- `for_each` to create multiple storage buckets
- Variables for deployment configuration
- Outputs for resource names and connection details

## Folder Structure

```text
assignment/aws/
├── main.tf
├── variables.tf
├── outputs.tf
├── README.md
└── modules/
    └── s3-bucket/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

## What Gets Created

- `raw`, `staged`, and `curated` S3 buckets with:
  - versioning enabled
  - default AES256 encryption
  - public access blocked
- One DynamoDB table named `{project_name}-{environment}-pipeline-metadata`

## Usage

```bash
cd lecture8/assignment/aws
terraform init
terraform plan
terraform apply
terraform output
```

When done:

```bash
terraform destroy
```

## Notes

- Bucket names include your AWS account ID so they are globally unique.
- DynamoDB is used as the database component for this assignment to keep the deployment simple and low-cost.
- If you want Terraform to delete non-empty buckets during `destroy`, set:

```bash
terraform apply -var="force_destroy_buckets=true"
```

## Suggested Submission Screenshots

- AWS S3 console showing the created buckets
- AWS DynamoDB console showing the metadata table
- `terraform output` showing bucket names and the table name
