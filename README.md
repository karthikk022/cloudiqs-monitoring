# CloudIQS Centralized Multi-Account Monitoring

A production-ready solution for monitoring multiple AWS customer accounts (single and multi-account) from a centralized hub.

## Quick Start

```bash
# 1. Open the live dashboard
open dashboard/index.html

# 2. Generate a compliance report
python scripts/report_generator.py

# 3. Run the data flow simulator
python scripts/simulate_data_flow.py
```

## Dashboard

![Dashboard Preview](dashboard/index.html)

The dashboard is a **fully self-contained HTML file** — opens in any browser, no backend needed. Shows:
- 5 simulated accounts (1 hub + 4 customers)
- Real-time security findings, compliance scores, cost data
- Interactive charts (severity distribution, compliance, costs, CPU trends)
- One-click report generation

## Architecture

```
Monitoring Hub (000000000001)
  ├── Security Hub Admin ← Findings from all member accounts
  ├── Config Aggregator ← Compliance from all accounts
  ├── CloudWatch Cross-Account Dashboard
  ├── Central S3 Bucket (findings/reports/logs/)
  ├── SNS Alerts
  └── IAM Cross-Account Role (with External ID)
       │
       ├── Customer A (000000000002) - Single Account
       ├── Customer B-Prod (000000000003) - Multi-Account
       ├── Customer B-Dev (000000000004) - Multi-Account
       └── Customer C (000000000005) - Multi-Account
```

## Project Structure

```
cloudiqs-monitoring/
├── terraform/                 # Infrastructure as Code
│   ├── modules/
│   │   ├── monitoring-account/   # Hub: S3, Security Hub, Config, IAM, SNS
│   │   └── member-account/       # Customer: Security Hub, Config, EC2, S3, IAM
│   └── environments/
│       ├── monitoring/           # Hub deployment
│       ├── customer-a/           # Single account
│       ├── customer-b-prod/      # Multi-account (production)
│       ├── customer-b-dev/       # Multi-account (development)
│       └── customer-c/           # Multi-account
├── dashboard/
│   └── index.html             # Live monitoring dashboard (self-contained)
├── scripts/
│   ├── report_generator.py    # Generates HTML compliance reports
│   └── simulate_data_flow.py  # Demonstrates cross-account data collection
├── docs/
│   ├── architecture.md        # Architecture documentation
│   └── demo-guide.md          # Step-by-step demo guide
├── output/                    # Generated reports
└── README.md
```

## Key Features

| Feature | Implementation |
|---------|---------------|
| Cross-account Security Hub | Security Hub administrator receives findings from all member accounts |
| Multi-account Config | Config Aggregator provides unified compliance view |
| Cross-account IAM | `sts:AssumeRole` with `ExternalId` condition for security |
| Central dashboard | CloudWatch cross-account dashboard + standalone HTML dashboard |
| Automated reporting | Lambda generates reports → stores in S3 → notifies via SNS |
| Sample resources | EC2 instances, S3 buckets, Lambda functions in each account |
| Monitoring alerts | CloudWatch alarms for CPU, unauthorized API calls |

## Terraform Deployment

```bash
# Deploy Monitoring Hub
cd terraform/environments/monitoring
terraform init
terraform plan
terraform apply

# Deploy Customer Accounts
cd ../customer-a
terraform init && terraform apply
cd ../customer-b-prod
terraform init && terraform apply
cd ../customer-b-dev
terraform init && terraform apply
cd ../customer-c
terraform init && terraform apply
```

## Customer Scenarios Covered

| Scenario | Example | Implementation |
|----------|---------|----------------|
| Single account customer | Customer A | One member account, one region |
| Multi-account customer | Customer B | Prod + Dev in separate accounts |
| Multi-region customer | Customer C | Resources in eu-west-1 |
| Hub account | Monitoring Hub | Security Hub admin, Config Aggregator |

## Sample Findings

| ID | Severity | Account | Description |
|----|----------|---------|-------------|
| CT-001 | CRITICAL | Customer B-Dev | CloudTrail logging disabled |
| S3-001 | HIGH | Customer A | S3 bucket public access blocked |
| CPU-001 | HIGH | Customer B-Prod | CPU > 80% sustained |
| SG-002 | MEDIUM | Customer B-Prod | Security group SSH open |
| EBS-001 | MEDIUM | Customer C | EBS encryption not enabled |

## Reporting

```bash
# Generate HTML compliance report
python scripts/report_generator.py --output cloudiqs-report.html

# Simulate cross-account data flow
python scripts/simulate_data_flow.py
```
