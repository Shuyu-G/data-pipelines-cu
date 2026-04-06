# Lecture 7 Assignment (AWS): Web Server + n8n

This Terraform project deploys one EC2 instance and runs two Docker containers:

1. `nginx:alpine` on port `8080` (web server)
2. `n8nio/n8n:latest` on port `5678` (n8n)

Dependency order is enforced in `user_data`:

- Install Docker
- Start web server container first
- Start n8n container second

## Prerequisites

- Terraform >= 1.0
- AWS account and valid credentials (`aws configure`)
- IAM permissions for EC2, VPC read, and Security Groups

## Usage

```bash
cd lecture7/assignment/aws
terraform init
terraform apply
```

After apply:

```bash
terraform output webserver_url
terraform output n8n_url
```

When done:

```bash
terraform destroy
```

## Optional variables

- `aws_region` (default: `eu-central-1`)
- `instance_type` (default: `t3.small`)
- `key_name` (default: empty)

Example:

```bash
terraform apply -var="aws_region=eu-central-1" -var="instance_type=t3.small"
```
