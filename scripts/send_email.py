"""Bonus: email the test report (SMTP settings come from environment variables / CI secrets)."""
import json
import os
import smtplib
from email.message import EmailMessage

report = json.load(open("report.json", encoding="utf-8"))
msg = EmailMessage()
msg["Subject"] = f"[CI] {report['overall_status'].upper()} - {report['repository']} @ {report['commit_sha'][:7]}"
msg["From"] = os.environ["SMTP_USER"]
msg["To"] = os.environ["EMAIL_TO"]

lines = [
    f"Commit:  {report['commit_sha']}",
    f"Branch:  {report['branch']}",
    f"Run ID:  {report['run_id']}",
    f"Result:  {report['overall_status']}",
    f"Total: {report['total']}  Passed: {report['passed']}  Failed: {report['failed']}",
    "",
]
for t in report["tests"]:
    extra = f" - {t['failure_message']}" if t["failure_message"] else ""
    lines.append(f"{t['result'].upper():7} {t['name']}{extra}")
msg.set_content("\n".join(lines))
msg.add_attachment(json.dumps(report, indent=2).encode(), maintype="application",
                   subtype="json", filename="test-report.json")

with smtplib.SMTP_SSL(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", "465"))) as s:
    s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
    s.send_message(msg)
print("email sent")
