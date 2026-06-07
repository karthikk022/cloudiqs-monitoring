terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "aws_region" {
  type        = string
  default     = "ap-south-1"
}

variable "account_id" {
  type        = string
}

variable "monitoring_account_id" {
  type        = string
  default     = "000000000001"
}

variable "customer_name" {
  type        = string
}

variable "environment" {
  type        = string
  default     = "production"
}

# Security Hub Member
resource "aws_securityhub_account" "member" {
  enable_default_standards = true
}

# Cross-Account IAM Role
resource "aws_iam_role" "monitoring_role" {
  name = "CloudIQS-Monitoring-Member-Access"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${var.monitoring_account_id}:root"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "sts:ExternalId" = "CloudIQS-Monitoring-${var.customer_name}"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "member_monitoring" {
  name = "member-account-monitoring"
  role = aws_iam_role.monitoring_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "securityhub:GetFindings",
          "config:DescribeConfigRules",
          "cloudwatch:GetMetricData",
          "cloudwatch:ListMetrics",
          "cloudwatch:DescribeAlarms",
          "logs:DescribeLogGroups",
          "logs:FilterLogEvents",
          "ec2:DescribeInstances",
          "ec2:DescribeSecurityGroups",
          "s3:ListAllMyBuckets"
        ]
        Resource = ["*"]
      }
    ]
  })
}

# AWS Config
resource "aws_config_configuration_recorder" "main" {
  name     = "${var.customer_name}-config-recorder"
  role_arn = aws_iam_role.config_role.arn
  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}

resource "aws_config_delivery_channel" "main" {
  name           = "${var.customer_name}-config-channel"
  s3_bucket_name = aws_s3_bucket.config_bucket.id
  depends_on     = [aws_config_configuration_recorder.main]
}

resource "aws_config_configuration_recorder_status" "main" {
  name       = aws_config_configuration_recorder.main.name
  is_enabled = true
  depends_on = [aws_config_delivery_channel.main]
}

resource "aws_s3_bucket" "config_bucket" {
  bucket        = "${var.customer_name}-config-bucket-${var.environment}"
  force_destroy = true
}

resource "aws_iam_role" "config_role" {
  name = "${var.customer_name}-config-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "config_policy" {
  role       = aws_iam_role.config_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSConfigRole"
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "unauthorized_api_calls" {
  alarm_name          = "${var.customer_name}-unauthorized-api-calls"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "NumberOfUnauthorizedAPICalls"
  namespace           = "AWS/CloudTrail"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "Alert on unauthorized API calls"
  alarm_actions       = []
}

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${var.customer_name}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "High CPU utilization alert"
  alarm_actions       = []
}

# Sample Resources
resource "aws_instance" "web_server" {
  count         = 2
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.medium"
  tags = {
    Name        = "${var.customer_name}-web-${count.index + 1}"
    Environment = var.environment
    Customer    = var.customer_name
  }
}

resource "aws_instance" "db_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.large"
  tags = {
    Name        = "${var.customer_name}-db-1"
    Environment = var.environment
    Customer    = var.customer_name
  }
}

resource "aws_s3_bucket" "app_data" {
  bucket        = "${var.customer_name}-app-data-${var.environment}"
  force_destroy = true
}

resource "aws_s3_bucket" "backups" {
  bucket        = "${var.customer_name}-backups-${var.environment}"
  force_destroy = true
}

resource "aws_sns_topic" "alerts" {
  name = "${var.customer_name}-alerts"
}

resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/cloudiqs/${var.customer_name}/${var.environment}"
  retention_in_days = 30
}

output "member_account_role_arn" {
  value = aws_iam_role.monitoring_role.arn
}

output "customer_name" {
  value = var.customer_name
}
