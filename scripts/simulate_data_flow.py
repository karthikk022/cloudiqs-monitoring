"""
CloudIQS Data Flow Simulator
Demonstrates how data moves from customer accounts to the monitoring hub.
Run: python simulate_data_flow.py

This simulates the cross-account data flow:
  1. Customer accounts generate findings/metrics
  2. Monitoring hub assumes IAM roles to collect data
  3. Data is aggregated and a report is generated
"""

import json
import os
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')

FINDINGS = {
    "000000000001": {
        "customer": "Monitoring Hub",
        "findings": [
            {"id": "IAM-001", "severity": "INFORMATIONAL", "title": "IAM password policy configured",
             "resource": "Account-wide", "status": "RESOLVED", "compliance": "PASSED"}
        ]
    },
    "000000000002": {
        "customer": "Customer A",
        "type": "Single Account",
        "region": "ap-south-1",
        "findings": [
            {"id": "S3-001", "severity": "HIGH", "title": "S3 bucket public access blocked",
             "resource": "customer-a-app-data-production", "status": "NEW", "compliance": "FAILED"}
        ],
        "metrics": {"cpu_avg": 60.3, "lambda_invocations": 320, "cost_estimated": 1200, "compliance_score": 85}
    },
    "000000000003": {
        "customer": "Customer B - Production",
        "type": "Multi-Account (Production)",
        "region": "us-east-1",
        "findings": [
            {"id": "SG-002", "severity": "MEDIUM", "title": "Security group SSH open to 0.0.0.0/0",
             "resource": "sg-12345", "status": "NEW", "compliance": "FAILED"},
            {"id": "CPU-001", "severity": "HIGH", "title": "CPU > 80% for 2 consecutive periods",
             "resource": "web-server-1", "status": "ACKNOWLEDGED", "compliance": "FAILED"}
        ],
        "metrics": {"cpu_avg": 86.8, "lambda_invocations": 850, "cost_estimated": 2450, "compliance_score": 62}
    },
    "000000000004": {
        "customer": "Customer B - Development",
        "type": "Multi-Account (Development)",
        "region": "ap-south-1",
        "findings": [
            {"id": "CT-001", "severity": "CRITICAL", "title": "CloudTrail logging disabled",
             "resource": "Account-wide", "status": "NEW", "compliance": "FAILED"}
        ],
        "metrics": {"cpu_avg": 11.9, "lambda_invocations": 45, "cost_estimated": 245, "compliance_score": 45}
    },
    "000000000005": {
        "customer": "Customer C",
        "type": "Multi-Account",
        "region": "eu-west-1",
        "findings": [
            {"id": "EBS-001", "severity": "MEDIUM", "title": "EBS encryption not enabled",
             "resource": "vol-abcdef123", "status": "NEW", "compliance": "FAILED"}
        ],
        "metrics": {"cpu_avg": 55.0, "lambda_invocations": 320, "cost_estimated": 3450, "compliance_score": 68}
    }
}


def simulate_cross_account_assume_role(account_id):
    """Simulates the monitoring account assuming a role in a member account."""
    print(f"  -> Monitoring Account assuming CloudIQS-Monitoring-Member-Access in account {account_id}")
    print(f"    Condition: sts:ExternalId = CloudIQS-Monitoring-{FINDINGS[account_id]['customer']}")
    return True


def collect_findings(account_id):
    """Simulates collecting Security Hub findings via cross-account API call."""
    print(f"  -> Calling securityhub:GetFindings in account {account_id}")
    return FINDINGS[account_id]["findings"]


def collect_metrics(account_id):
    """Simulates collecting CloudWatch metrics via cross-account API call."""
    print(f"  -> Calling cloudwatch:GetMetricData in account {account_id}")
    return FINDINGS[account_id].get("metrics", {})


def generate_report(all_data):
    """Generates a consolidated JSON report similar to what the Lambda would produce."""
    total_findings = 0
    critical = high = medium = low = 0
    total_cost = 0
    account_reports = []

    for acct_id, data in all_data.items():
        findings = data.get("findings", [])
        metrics = data.get("metrics", {})
        total_findings += len(findings)
        total_cost += metrics.get("cost_estimated", 0)

        for f in findings:
            s = f["severity"]
            if s == "CRITICAL": critical += 1
            elif s == "HIGH": high += 1
            elif s == "MEDIUM": medium += 1
            else: low += 1

        account_reports.append({
            "account_id": acct_id,
            "customer": data["customer"],
            "type": data.get("type", "Hub"),
            "region": data.get("region", "ap-south-1"),
            "findings_count": len(findings),
            "compliance_score": metrics.get("compliance_score", 100),
            "monthly_cost": metrics.get("cost_estimated", 0),
            "findings": findings
        })

    report = {
        "report_id": f"cloudiqs-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "generated_at": datetime.now().isoformat(),
        "report_type": "Cross-Account Compliance & Security Summary",
        "simulated_data_flow": [
            "1. Customer accounts generate Security Hub findings and CloudWatch metrics",
            "2. Monitoring Hub assumes IAM role (sts:AssumeRole) into each member account",
            "3. Findings collected via securityhub:GetFindings (cross-account)",
            "4. Metrics collected via cloudwatch:GetMetricData (cross-account)",
            "5. Data aggregated into central S3 bucket",
            "6. Report generated and stored in s3://cloudiqs-central-monitoring-production/reports/"
        ],
        "summary": {
            "total_accounts": len(all_data),
            "total_findings": total_findings,
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "total_monthly_cost": total_cost,
            "overall_compliance_pct": round(
                sum(a["compliance_score"] for a in account_reports) / len(account_reports), 1)
        },
        "accounts": account_reports,
        "recommendations": [
            "Enable CloudTrail in Customer B-Dev immediately (CRITICAL)",
            "Restrict SSH inbound rules in Customer B-Prod security groups",
            "Enable EBS encryption by default for Customer C",
            "Review S3 bucket policies for Customer A",
            "Set up budget alerts for Customer C ($3,450/mo)"
        ]
    }
    return report


def main():
    print("=" * 60)
    print("  CloudIQS Multi-Account Data Flow Simulation")
    print("  Demonstrating Cross-Account Monitoring Pattern")
    print("=" * 60)

    print("\n[STEP 1] Central S3 bucket created (cloudiqs-central-monitoring-production)")
    print("[STEP 2] Security Hub admin enabled with cross-account members")
    print("[STEP 3] Config Aggregator configured for multi-account compliance")
    print("[STEP 4] Cross-account IAM roles deployed in all member accounts\n")

    print("--- Beginning Cross-Account Data Collection ---\n")

    all_data = {}

    for acct_id in FINDINGS:
        data = FINDINGS[acct_id]
        print(f"\n{'=' * 50}")
        print(f"  Processing: {data['customer']} ({acct_id})")
        print(f"{'=' * 50}")

        if data.get("type") != "Hub":
            simulate_cross_account_assume_role(acct_id)

        findings = collect_findings(acct_id)
        metrics = collect_metrics(acct_id)

        print(f"  -> Collected {len(findings)} findings")
        for f in findings:
            print(f"    [{f['severity']:12s}] {f['title']}")

        if metrics:
            print(f"  -> Metrics: CPU {metrics.get('cpu_avg','N/A')}% | "
                  f"Lambda {metrics.get('lambda_invocations','N/A')} | "
                  f"Compliance {metrics.get('compliance_score','N/A')}%")

        print(f"  -> Data written to s3://cloudiqs-central-monitoring-production/findings/{acct_id}/")
        all_data[acct_id] = data

    print(f"\n{'=' * 60}")
    print("  Generating Consolidated Report...")
    print(f"{'=' * 60}")

    report = generate_report(all_data)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, f"cloudiqs-report-{datetime.now().strftime('%Y%m%d')}.json")
    with open(filepath, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport written to: {filepath}")
    print(f"\nReport Summary:")
    print(f"  Accounts monitored: {report['summary']['total_accounts']}")
    print(f"  Total findings:     {report['summary']['total_findings']}")
    print(f"    Critical: {report['summary']['critical']} | "
          f"High: {report['summary']['high']} | "
          f"Medium: {report['summary']['medium']} | "
          f"Low: {report['summary']['low']}")
    print(f"  Compliance score:   {report['summary']['overall_compliance_pct']}%")
    print(f"  Monthly cost:       ${report['summary']['total_monthly_cost']:,.0f}")
    print(f"\n{'=' * 60}")
    print("  Simulation Complete. Open dashboard/index.html to view.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
