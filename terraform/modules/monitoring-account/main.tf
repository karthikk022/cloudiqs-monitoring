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
  default     = "000000000001"
}

variable "member_account_ids" {
  type        = list(string)
  default     = ["000000000002", "000000000003", "000000000004", "000000000005"]
}

variable "environment" {
  type        = string
  default     = "production"
}

# Central S3 Bucket
resource "aws_s3_bucket" "central_logs" {
  bucket        = "cloudiqs-central-monitoring-${var.environment}"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "central_logs" {
  bucket = aws_s3_bucket.central_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "central_logs" {
  bucket = aws_s3_bucket.central_logs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "central_logs" {
  bucket = aws_s3_bucket.central_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "findings_prefix" {
  for_each = toset(var.member_account_ids)
  bucket   = aws_s3_bucket.central_logs.id
  key      = "findings/${each.value}/"
}

resource "aws_s3_object" "reports_prefix" {
  for_each = toset(var.member_account_ids)
  bucket   = aws_s3_bucket.central_logs.id
  key      = "reports/${each.value}/"
}

resource "aws_s3_object" "logs_prefix" {
  for_each = toset(var.member_account_ids)
  bucket   = aws_s3_bucket.central_logs.id
  key      = "logs/${each.value}/"
}

# Security Hub
resource "aws_securityhub_account" "main" {
  enable_default_standards = true
}

resource "aws_securityhub_member" "members" {
  for_each   = toset(var.member_account_ids)
  account_id = each.value
  email      = "customer-${each.value}@cloudiqs.com"
  invite     = false
}

# Config Aggregator
resource "aws_config_configuration_aggregator" "org_aggregator" {
  name = "cloudiqs-multi-account-aggregator"
  account_aggregation_source {
    account_ids = var.member_account_ids
    all_regions = true
  }
}

resource "aws_config_aggregate_authorization" "member_auth" {
  for_each   = toset(var.member_account_ids)
  account_id = each.value
  region     = var.aws_region
}

# SNS Topic
resource "aws_sns_topic" "alerts" {
  name = "cloudiqs-central-alerts"
}

# IAM Cross-Account Role
resource "aws_iam_role" "cross_account_monitoring" {
  name = "CloudIQS-Monitoring-Access"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${var.account_id}:root"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "sts:ExternalId" = "CloudIQS-Monitoring-${var.environment}"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "monitoring_read_only" {
  name = "monitoring-read-only-access"
  role = aws_iam_role.cross_account_monitoring.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "securityhub:GetFindings",
          "securityhub:GetInsights",
          "config:GetComplianceDetailsByConfigRule",
          "cloudwatch:GetMetricData",
          "cloudwatch:ListMetrics",
          "cloudwatch:DescribeAlarms",
          "logs:DescribeLogGroups",
          "logs:FilterLogEvents",
          "s3:GetObject",
          "s3:ListBucket",
          "ec2:DescribeInstances",
          "ec2:DescribeSecurityGroups"
        ]
        Resource = ["*"]
      }
    ]
  })
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "central" {
  dashboard_name = "CloudIQS-MultiAccount-Monitoring"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "text", x = 0, y = 0, width = 24, height = 2
        properties = {
          markdown = "# CloudIQS Central Monitoring\n## Multi-Account Overview\n**Environment:** ${var.environment}"
        }
      },
      {
        type = "metric", x = 0, y = 2, width = 12, height = 6
        properties = {
          metrics = flatten([for a in var.member_account_ids : [
            ["AWS/SecurityHub", "FindingCount", { accountId = a, stat = "Sum", label = "Account ${a}" }]
          ]]),
          period = 300, stat = "Sum", region = var.aws_region,
          title = "Security Hub Findings by Account"
        }
      },
      {
        type = "metric", x = 12, y = 2, width = 12, height = 6
        properties = {
          metrics = flatten([for a in var.member_account_ids : [
            ["AWS/Config", "ComplianceScore", { accountId = a, stat = "Average", label = "Account ${a}" }]
          ]]),
          period = 300, stat = "Average", region = var.aws_region,
          title = "Compliance Score by Account"
        }
      },
      {
        type = "metric", x = 0, y = 8, width = 8, height = 6
        properties = {
          metrics = flatten([for a in var.member_account_ids : [
            ["AWS/Billing", "EstimatedCharges", { accountId = a, stat = "Maximum", label = "Account ${a}" }]
          ]]),
          period = 86400, stat = "Maximum", region = var.aws_region,
          title = "Estimated Cost by Account"
        }
      },
      {
        type = "metric", x = 8, y = 8, width = 8, height = 6
        properties = {
          metrics = flatten([for a in var.member_account_ids : [
            ["AWS/Lambda", "Invocations", { accountId = a, stat = "Sum", label = "Account ${a}" }]
          ]]),
          period = 300, stat = "Sum", region = var.aws_region,
          title = "Lambda Invocations by Account"
        }
      },
      {
        type = "metric", x = 16, y = 8, width = 8, height = 6
        properties = {
          metrics = flatten([for a in var.member_account_ids : [
            ["AWS/Logs", "IncomingBytes", { accountId = a, stat = "Sum", label = "Account ${a}" }]
          ]]),
          period = 300, stat = "Sum", region = var.aws_region,
          title = "Log Volume by Account"
        }
      }
    ]
  })
}

output "central_bucket" {
  value = aws_s3_bucket.central_logs.id
}

output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}

output "cross_account_role_arn" {
  value = aws_iam_role.cross_account_monitoring.arn
}
