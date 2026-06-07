# CloudIQS Centralized Multi-Account Monitoring

## Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                     MONITORING HUB (000000000001)                      │
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐     │
│  │ Security Hub │  │ Config       │  │ CloudWatch               │     │
│  │ Administrator│  │ Aggregator   │  │ Cross-Account Dashboard   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────────┘     │
│         │                │                      │                      │
│  ┌──────┴────────────────┴──────────────────────┴──────────────────┐  │
│  │              Central S3 Bucket (findings/reports/logs/)          │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  SNS Alerts ← Lambda Report Generator                            │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  IAM Role: CloudIQS-Monitoring-Access                                  │
│  (sts:AssumeRole + ExternalId condition)                               │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
              Cross-Account IAM Roles (sts:AssumeRole)
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  CUSTOMER A      │  │  CUSTOMER B      │  │  CUSTOMER C      │
│  Single Account  │  │  Multi-Account   │  │  Multi-Account   │
│  000000000002    │  │  000000000003    │  │  000000000005    │
│  ap-south-1      │  │  000000000004    │  │  eu-west-1       │
│                  │  │  (prod + dev)    │  │                  │
│  • Security Hub  │  │                  │  │  • Security Hub  │
│  • Config        │  │  • Security Hub  │  │  • Config        │
│  • CloudWatch    │  │  • Config        │  │  • CloudWatch    │
│  • EC2, S3       │  │  • CloudWatch    │  │  • EC2, S3       │
│  • SNS, Lambda   │  │  • EC2, Lambda   │  │  • Lambda        │
└──────────────────┘  │  • S3, Logs      │  └──────────────────┘
                       └──────────────────┘
```

## Customer Account Structure

| Customer | Account ID | Type | Region | Environments | Services |
|----------|-----------|------|--------|-------------|----------|
| Monitoring Hub | 000000000001 | Management | ap-south-1 | Production | Security Hub Admin, Config Aggregator, CloudWatch Dashboard, S3, SNS, IAM |
| Customer A | 000000000002 | Single | ap-south-1 | Production | Security Hub Member, Config, CloudWatch, EC2, S3, SNS |
| Customer B-Prod | 000000000003 | Multi-Account | us-east-1 | Production | Security Hub Member, Config, CloudWatch, EC2, S3, SNS |
| Customer B-Dev | 000000000004 | Multi-Account | ap-south-1 | Development | Security Hub Member, Config, CloudWatch, EC2, S3, SNS |
| Customer C | 000000000005 | Multi-Account | eu-west-1 | Production | Security Hub Member, Config, CloudWatch, EC2, S3, SNS |

## Cross-Account Data Flow

1. **Initiation**: Monitoring Hub initiates data collection by assuming IAM roles in member accounts
2. **Authentication**: `sts:AssumeRole` with `ExternalId` condition prevents confused deputy attacks
3. **Collection**: API calls made with temporary credentials to collect:
   - Security Hub findings (`GetFindings`)
   - Config compliance scores (`DescribeComplianceByConfigRule`)
   - CloudWatch metrics (`GetMetricData`, `ListMetrics`)
   - CloudWatch logs (`FilterLogEvents`)
4. **Storage**: Data written to central S3 bucket organized by account ID
5. **Reporting**: Lambda function generates periodic reports and publishes to SNS

## Key AWS Services Used

### Monitoring Hub
- **AWS Security Hub** - Central administrator for cross-account findings
- **AWS Config Aggregator** - Multi-account compliance view
- **Amazon CloudWatch** - Cross-account dashboards and metrics
- **AWS IAM** - Cross-account roles with External ID
- **Amazon S3** - Centralized log and report storage
- **Amazon SNS** - Alert notifications
- **AWS Lambda** - Automated report generation

### Member Accounts
- **AWS Security Hub** - Member accounts sending findings to admin
- **AWS Config** - Resource compliance recording
- **Amazon CloudWatch** - Metrics, logs, and alarms
- **Amazon EC2** - Sample compute resources
- **Amazon S3** - Application data and backups
- **AWS IAM** - Cross-account role for monitoring access

## Security Considerations

- **External ID**: Prevents confused deputy attacks on cross-account roles
- **Least Privilege**: Read-only policies for monitoring account
- **Encryption at Rest**: S3 SSE enabled on central bucket
- **Public Access Blocked**: All buckets have public access blocked
- **CloudTrail**: Recommended enabled for API auditing (missing in finding CT-001)

## Deployment

```bash
# Initialize and deploy monitoring hub
cd terraform/environments/monitoring
terraform init
terraform apply

# Deploy each customer account
cd terraform/environments/customer-a
terraform init && terraform apply
# Repeat for customer-b-prod, customer-b-dev, customer-c
```

## Local Demo

```bash
# Generate a sample compliance report
python scripts/report_generator.py
# Open dashboard/index.html in browser
# Run data flow simulator
python scripts/simulate_data_flow.py
```
