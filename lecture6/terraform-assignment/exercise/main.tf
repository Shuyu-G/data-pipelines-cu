terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

variable "aws_region" {
  description = "AWS region to deploy the webserver into."
  type        = string
  default     = "eu-central-1"
}

variable "instance_type" {
  description = "EC2 instance type for the nginx webserver."
  type        = string
  default     = "t3.micro"
}

provider "aws" {
  region = var.aws_region
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

locals {
  project_name = "terraform-assignment-webserver"
  html_content = <<-HTML
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>My First Terraform Webserver on AWS</title>
      <style>
        body {
          margin: 0;
          min-height: 100vh;
          display: grid;
          place-items: center;
          background: linear-gradient(135deg, #0f172a, #1d4ed8);
          color: #e2e8f0;
          font-family: Arial, sans-serif;
        }
        main {
          max-width: 720px;
          padding: 48px;
          border-radius: 24px;
          background: rgba(15, 23, 42, 0.75);
          box-shadow: 0 24px 60px rgba(15, 23, 42, 0.4);
        }
        h1 {
          margin-top: 0;
          font-size: 2.6rem;
        }
        p {
          line-height: 1.6;
          font-size: 1.1rem;
        }
        strong {
          color: #f8fafc;
        }
      </style>
    </head>
    <body>
      <main>
        <h1>Hello from Terraform on AWS!</h1>
        <p>This page was provisioned with <strong>Terraform</strong>, served by <strong>nginx</strong>, and deployed on an <strong>Amazon EC2</strong> instance.</p>
        <p>Student: <strong>Shuyu Gui</strong></p>
        <p>Email: <strong>sgui@constructor.university</strong></p>
        <p>Course: Data Pipelines CU, Lecture 6 Terraform Assignment.</p>
      </main>
    </body>
    </html>
  HTML
}

resource "local_file" "index_html" {
  content  = local.html_content
  filename = "${path.module}/index.html"
}

resource "aws_vpc" "web" {
  cidr_block           = "10.42.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${local.project_name}-vpc"
  }
}

resource "aws_internet_gateway" "web" {
  vpc_id = aws_vpc.web.id

  tags = {
    Name = "${local.project_name}-igw"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.web.id
  cidr_block              = "10.42.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "${local.project_name}-public-subnet"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.web.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.web.id
  }

  tags = {
    Name = "${local.project_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "web" {
  name        = "${local.project_name}-sg"
  description = "Allow HTTP traffic to the Terraform assignment webserver"
  vpc_id      = aws_vpc.web.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.project_name}-sg"
  }
}

resource "aws_instance" "web" {
  ami                         = data.aws_ami.amazon_linux_2023.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web.id]
  associate_public_ip_address = true
  user_data_replace_on_change = true

  user_data = <<-EOF
    #!/bin/bash
    set -euxo pipefail

    dnf install -y nginx

    cat <<'HTML' > /usr/share/nginx/html/index.html
    ${local.html_content}
    HTML

    systemctl enable nginx
    systemctl restart nginx
  EOF

  depends_on = [
    aws_route_table_association.public,
    local_file.index_html
  ]

  tags = {
    Name = local.project_name
  }
}

output "website_url" {
  value       = "http://${aws_instance.web.public_ip}"
  description = "Public URL for the deployed HTML page."
}

output "public_ip" {
  value       = aws_instance.web.public_ip
  description = "Public IPv4 address of the EC2 instance."
}

output "instance_id" {
  value       = aws_instance.web.id
  description = "EC2 instance ID for the webserver."
}
