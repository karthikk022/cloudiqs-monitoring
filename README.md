<p align="center">
  <h1 align="center">CloudIQS Centralized Multi-Account Monitoring</h1>
  <p align="center">
    Cross-account AWS monitoring for single and multi-account customers
    <br />
    <a href="https://github.com/karthikk022/cloudiqs-monitoring"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="#live-demo">Live Demo</a>
    ·
    <a href="docs/architecture.md">Architecture</a>
    ·
    <a href="docs/demo-guide.md">Demo Guide</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Terraform-7B42BC?logo=terraform&logoColor=white" />
  <img src="https://img.shields.io/badge/AWS-FF9900?logo=amazonaws&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/moto-FF6F00?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
</p>

---

## Task

Build a centralized environment to monitor customer AWS accounts — single and multi-account — and provide reporting with findings access.

## Solution

A centralized **Monitoring Hub** account that aggregates security, compliance, cost, and performance data from customer accounts using cross-account IAM roles, Security Hub aggregation, Config Aggregator, and CloudWatch cross-account dashboards.

## Live Demo

**No AWS account needed.** Uses [moto](https://github.com/getmoto/moto) to mock AWS services — makes real boto3 API calls locally.

```bash
pip install moto boto3
python scripts/live_demo.py
```

What it does:
- Creates monitoring hub (S3, Security Hub, Config Aggregator, IAM, SNS)
- Creates 4 customer accounts with resources
- Generates Security Hub findings (1 CRITICAL, 2 HIGH, 2 MEDIUM)
- Collects CloudWatch metrics cross-account
- Generates consolidated compliance report in S3

## Dashboard

Open `dashboard/index.html` in any browser — fully self-contained.

Shows:
- 5 accounts (1 hub + 4 customers)
- Live security findings, compliance scores, costs
- Interactive charts (severity, compliance, costs, CPU trends)
- One-click report generation

## Architecture

```
MONITORING HUB (000000000001)
  |-- Security Hub Admin <-- Findings from 4 member accounts
  |-- Config Aggregator <-- Multi-account compliance
  |-- CloudWatch Dashboard <-- Cross-account metrics
  |-- S3 Central Bucket (findings/reports/logs/)
  |-- SNS Alerts
  |-- IAM Cross-Account Role (sts:AssumeRole + ExternalId)
        |
        |-- Customer A (000000000002) -- Single Account (ap-south-1)
        |-- Customer B-Prod (000000000003) -- Multi-Account (us-east-1)
        |-- Customer B-Dev (000000000004) -- Multi-Account (ap-south-1)
        |-- Customer C (000000000005) -- Multi-Account (eu-west-1)
```

## Customer Scenarios

| Scenario | Example | Implementation |
|----------|---------|----------------|
| Single account | Customer A | 1 member account, 1 region |
| Multi-account (prod+dev) | Customer B | 2 accounts, separate regions |
| Multi-account, multi-region | Customer C | 1 account, eu-west-1 |
| Hub / management | Monitoring Hub | Security Hub admin, Config Aggregator |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Infrastructure as Code** | Terraform (AWS provider v5) |
| **Security** | AWS Security Hub (cross-account) |
| **Compliance** | AWS Config Aggregator |
| **Monitoring** | Amazon CloudWatch (cross-account) |
| **Storage** | Amazon S3 (centralized, encrypted) |
| **Alerting** | Amazon SNS |
| **Compute (sample)** | Amazon EC2 |
| **Local Demo** | Python + moto + boto3 |
| **Dashboard** | HTML + Chart.js (self-contained) |
| **Reporting** | Python report generator |

## Security

- **External ID** on all cross-account IAM roles (prevents confused deputy)
- **Least privilege** read-only policies for monitoring account
- **Encryption at rest** on central S3 bucket (SSE-AES256)
- **Public access blocked** on all buckets

## Sample Findings

| ID | Severity | Account | Finding |
|----|----------|---------|---------|
| CT-001 | **CRITICAL** | Customer B-Dev | CloudTrail logging disabled |
| S3-001 | **HIGH** | Customer A | S3 bucket public access blocked |
| CPU-001 | **HIGH** | Customer B-Prod | CPU > 80% sustained |
| SG-002 | **MEDIUM** | Customer B-Prod | Security group SSH open to 0.0.0.0/0 |
| EBS-001 | **MEDIUM** | Customer C | EBS encryption not enabled |

## Project Structure

```
cloudiqs-monitoring/
  terraform/modules/
    monitoring-account/        # Hub: S3, Security Hub, Config, IAM, SNS
    member-account/            # Customer: Security Hub, Config, EC2, IAM
  terraform/environments/
    monitoring/                # Hub deployment
    customer-a/                # Single account customer
    customer-b-prod/           # Multi-account (production)
    customer-b-dev/            # Multi-account (development)
    customer-c/                # Multi-account
  dashboard/index.html         # Live dashboard (self-contained)
  scripts/
    live_demo.py               # Real boto3 API calls with moto
    report_generator.py        # HTML compliance report generator
    simulate_data_flow.py      # Cross-account data flow simulator
  docs/
    architecture.md            # Architecture documentation
    demo-guide.md              # Step-by-step demo script
```

## Terraform Deployment

```bash
# Deploy Monitoring Hub
cd terraform/environments/monitoring
terraform init && terraform apply

# Deploy Customer Accounts
cd ../customer-a && terraform init && terraform apply
cd ../customer-b-prod && terraform init && terraform apply
cd ../customer-b-dev && terraform init && terraform apply
cd ../customer-c && terraform init && terraform apply
```

## Generate Reports

```bash
python scripts/report_generator.py --output cloudiqs-report.html
```

## Author

**Karthick Raja C** — AWS DevOps Engineer · MLOps · 2 Years

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin&logoColor=white)](https://linkedin.com/in/karthickrajac)
[![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white)](https://github.com/karthikk022)
