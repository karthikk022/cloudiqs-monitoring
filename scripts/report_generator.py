"""
CloudIQS Report Generator
Generates comprehensive HTML compliance reports for all monitored accounts.
Usage: python report_generator.py [--output report.html]
"""

import json
import os
import argparse
from datetime import datetime

REPORT_DATA = {
    "generated_at": datetime.now().isoformat(),
    "report_period": "June 1-7, 2026",
    "pipeline": [
        "1. Security Hub findings collected from 4 member accounts via cross-account API calls",
        "2. Config compliance scores aggregated via Config Aggregator",
        "3. CloudWatch metrics pulled across accounts via GetMetricData",
        "4. Data normalized and written to central S3 bucket",
        "5. Lambda triggered to generate consolidated report"
    ],
    "overall_summary": {
        "total_accounts": 5,
        "accounts_with_findings": 4,
        "total_findings": 5,
        "critical": 1,
        "high": 2,
        "medium": 2,
        "low": 0,
        "overall_compliance_pct": 72
    },
    "accounts": [
        {
            "name": "Monitoring Hub",
            "account_id": "000000000001", "type": "Hub", "region": "ap-south-1",
            "status": "Healthy", "compliance_pct": 100, "findings": 1, "monthly_cost": 0,
            "critical_issues": []
        },
        {
            "name": "Customer A",
            "account_id": "000000000002", "type": "Single Account", "region": "ap-south-1",
            "status": "Good", "compliance_pct": 85, "findings": 1, "monthly_cost": 1200,
            "critical_issues": [
                {"severity": "HIGH", "title": "S3 bucket public access blocked",
                 "resource": "customer-a-app-data-production"}
            ]
        },
        {
            "name": "Customer B - Production",
            "account_id": "000000000003", "type": "Multi-Account (Prod)", "region": "us-east-1",
            "status": "Warning", "compliance_pct": 62, "findings": 2, "monthly_cost": 2450,
            "critical_issues": [
                {"severity": "HIGH", "title": "High CPU utilization >80%", "resource": "web-server-1"},
                {"severity": "MEDIUM", "title": "Security group SSH open to 0.0.0.0/0", "resource": "sg-12345"}
            ]
        },
        {
            "name": "Customer B - Development",
            "account_id": "000000000004", "type": "Multi-Account (Dev)", "region": "ap-south-1",
            "status": "Critical", "compliance_pct": 45, "findings": 1, "monthly_cost": 245,
            "critical_issues": [
                {"severity": "CRITICAL", "title": "CloudTrail logging disabled", "resource": "Account-wide"}
            ]
        },
        {
            "name": "Customer C",
            "account_id": "000000000005", "type": "Multi-Account", "region": "eu-west-1",
            "status": "Good", "compliance_pct": 68, "findings": 1, "monthly_cost": 3450,
            "critical_issues": [
                {"severity": "MEDIUM", "title": "EBS encryption not enabled", "resource": "vol-abcdef123"}
            ]
        }
    ],
    "cost_summary": {
        "total_monthly": 7345,
        "highest_customer": "Customer C",
        "highest_cost": 3450,
        "average_per_account": 1836
    },
    "recommendations": [
        "[CRITICAL] Enable CloudTrail in Customer B-Dev account immediately",
        "[HIGH] Restrict SSH inbound rules in Customer B-Prod security groups",
        "[MEDIUM] Enable EBS encryption by default for Customer C",
        "[HIGH] Review S3 bucket policies for Customer A",
        "[LOW] Set up budget alerts for Customer C (highest cost at $3,450/mo)"
    ]
}


def generate_html(data):
    accounts = data["accounts"]
    s = data["overall_summary"]
    c = data["cost_summary"]

    findings_rows = ""
    for acct in accounts:
        for issue in acct.get("critical_issues", []):
            sv = {"CRITICAL": "dc3545", "HIGH": "fd7e14", "MEDIUM": "ffc107", "LOW": "28a745"}
            findings_rows += f"""
            <tr><td>{acct['name']}</td>
            <td><span style="background:#{sv.get(issue['severity'],'6c757d')};color:#fff;padding:1px 6px;border-radius:3px;font-size:11px">{issue['severity']}</span></td>
            <td>{issue['title']}</td><td style="font-family:monospace;font-size:12px">{issue['resource']}</td></tr>"""

    bar = f"""
    <div style="display:flex;height:22px;border-radius:11px;overflow:hidden;margin:10px 0">
        <div style="background:#dc3545;flex:{max(s['critical'],1)};text-align:center;color:#fff;font-size:11px;line-height:22px">Critical: {s['critical']}</div>
        <div style="background:#fd7e14;flex:{max(s['high'],1)};text-align:center;color:#fff;font-size:11px;line-height:22px">High: {s['high']}</div>
        <div style="background:#ffc107;flex:{max(s['medium'],1)};text-align:center;color:#000;font-size:11px;line-height:22px">Medium: {s['medium']}</div>
        <div style="background:#28a745;flex:{max(s['low'],1)};text-align:center;color:#fff;font-size:11px;line-height:22px">Low: {s['low']}</div>
    </div>"""

    st = {"Healthy": "28a745", "Good": "17a2b8", "Warning": "ffc107", "Critical": "dc3545"}
    acct_rows = ""
    for a in accounts:
        color = st.get(a["status"], "6c757d")
        acct_rows += f"""
        <tr><td>{a['name']}</td><td style="font-family:monospace">{a['account_id']}</td>
        <td>{a['type']}</td><td><span style="background:#{color};color:#fff;padding:1px 8px;border-radius:3px;font-size:11px">{a['status']}</span></td>
        <td>{a['compliance_pct']}%</td><td>{a['findings']}</td><td>${a['monthly_cost']:,.0f}</td></tr>"""

    recs = "\n".join(f"<li>{r}</li>" for r in data["recommendations"])

    pipeline = "\n".join(f"<li>{p}</li>" for p in data.get("pipeline", []))

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>CloudIQS Weekly Compliance Report</title>
<style>
body {{ font-family:'Segoe UI',Arial,sans-serif; margin:20px; color:#333; }}
.header {{ border-bottom:3px solid #0d6efd; padding-bottom:10px; margin-bottom:20px; }}
.header h1 {{ margin:0; color:#0d6efd; font-size:22px; }}
.header .meta {{ color:#6c757d; font-size:13px; }}
table {{ width:100%; border-collapse:collapse; margin:12px 0; }}
th,td {{ padding:7px 10px; text-align:left; border-bottom:1px solid #dee2e6; font-size:13px; }}
th {{ background:#f8f9fa; font-weight:600; }}
.section {{ background:#f8f9fa; padding:8px 14px; margin:18px 0 10px; border-left:4px solid #0d6efd; font-weight:600; font-size:15px; }}
.cards {{ display:flex; gap:12px; flex-wrap:wrap; margin:12px 0; }}
.card {{ flex:1; min-width:100px; padding:12px; border:1px solid #dee2e6; border-radius:8px; text-align:center; }}
.card .num {{ font-size:24px; font-weight:700; }}
.card .lbl {{ font-size:10px; text-transform:uppercase; color:#6c757d; margin-top:3px; }}
.footer {{ margin-top:25px; padding-top:12px; border-top:1px solid #dee2e6; text-align:center; color:#6c757d; font-size:11px; }}
</style></head>
<body>
<div class="header"><h1>CloudIQS Weekly Compliance & Security Report</h1><div class="meta">Period: {data['report_period']} | Generated: {data['generated_at'][:10]}</div></div>

<div class="section">Data Pipeline</div>
<ol style="font-size:13px;color:#555">{pipeline}</ol>

<div class="section">Executive Summary</div>
<div class="cards">
<div class="card"><div class="num">{s['total_accounts']}</div><div class="lbl">Accounts</div></div>
<div class="card"><div class="num">{s['total_findings']}</div><div class="lbl">Findings</div></div>
<div class="card"><div class="num" style="color:#dc3545">{s['critical']}</div><div class="lbl">Critical</div></div>
<div class="card"><div class="num" style="color:#fd7e14">{s['high']}</div><div class="lbl">High</div></div>
<div class="card"><div class="num">{s['overall_compliance_pct']}%</div><div class="lbl">Compliance</div></div>
<div class="card"><div class="num">${c['total_monthly']:,.0f}</div><div class="lbl">Monthly Cost</div></div>
</div>

<div class="section">Findings by Severity</div>{bar}

<div class="section">Account Overview</div>
<table><tr><th>Customer</th><th>Account ID</th><th>Type</th><th>Status</th><th>Compliance</th><th>Findings</th><th>Cost</th></tr>{acct_rows}</table>

<div class="section">Open Findings</div>
<table><tr><th>Account</th><th>Severity</th><th>Finding</th><th>Resource</th></tr>{findings_rows}</table>

<div class="section">Recommendations</div>
<ol>{recs}</ol>

<div class="section">Cost Summary</div>
<table><tr><td>Total Monthly Cost</td><td><strong>${c['total_monthly']:,.0f}</strong></td></tr>
<tr><td>Highest Cost Customer</td><td>{c['highest_customer']} (${c['highest_cost']:,.0f}/mo)</td></tr>
<tr><td>Average per Account</td><td>${c['average_per_account']:,.0f}</td></tr></table>

<div class="footer">CloudIQS Central Monitoring · Confidential · Generated {data['generated_at'][:10]}</div>
</body></html>"""


def main():
    parser = argparse.ArgumentParser(description="CloudIQS Report Generator")
    parser.add_argument("--output", "-o", default="cloudiqs-report.html")
    args = parser.parse_args()

    html = generate_html(REPORT_DATA)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report generated: {args.output}")
    print(f"Open in browser to view the full compliance summary")


if __name__ == "__main__":
    main()
