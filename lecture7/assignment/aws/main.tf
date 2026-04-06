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

locals {
  key_name_value = var.key_name != "" ? var.key_name : null

  bootstrap_script = <<-EOT
    #!/bin/bash
    set -euo pipefail

    yum update -y
    yum install -y docker
    systemctl enable docker
    systemctl start docker

    usermod -aG docker ec2-user || true

    docker rm -f lecture7-webserver lecture7-n8n || true

    # 1) Start dependency first: web server
    docker run -d \
      --name lecture7-webserver \
      --restart unless-stopped \
      -p 8080:80 \
      nginx:alpine

    # 2) Start n8n only after web server
    docker run -d \
      --name lecture7-n8n \
      --restart unless-stopped \
      -p 5678:5678 \
      -e N8N_HOST=0.0.0.0 \
      -e N8N_PORT=5678 \
      -e N8N_PROTOCOL=http \
      -e N8N_SECURE_COOKIE=false \
      -e GENERIC_TIMEZONE=UTC \
      n8nio/n8n:latest
  EOT
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_security_group" "lecture7_web_n8n" {
  name_prefix = "lecture7-web-n8n-"
  description = "Allow HTTP ports for lecture7 assignment"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "Web server"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "n8n"
    from_port   = 5678
    to_port     = 5678
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
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
    Name = "lecture7-web-n8n-sg"
  }
}

resource "aws_instance" "web_n8n_host" {
  ami                         = data.aws_ami.amazon_linux_2023.id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.lecture7_web_n8n.id]
  associate_public_ip_address = true
  key_name                    = local.key_name_value

  user_data                   = local.bootstrap_script
  user_data_replace_on_change = true

  tags = {
    Name = "lecture7-web-n8n"
  }
}
