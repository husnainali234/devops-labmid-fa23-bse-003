"""Build report.json from pytest's results.xml (JUnit) plus GitHub Actions metadata."""
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

tests = []
root = ET.parse("results.xml").getroot()
for case in root.iter("testcase"):
    problem = case.find("failure")
    if problem is None:
        problem = case.find("error")
    failed = problem is not None
    tests.append({
        "name": case.get("name"),
        "result": "failed" if failed else "passed",
        "failure_message": (problem.get("message") if failed else None),
    })

passed = sum(t["result"] == "passed" for t in tests)
report = {
    "repository": os.environ.get("GITHUB_REPOSITORY", "local/repo"),
    "branch": os.environ.get("GITHUB_REF_NAME", "local"),
    "commit_sha": os.environ.get("GITHUB_SHA", "local"),
    "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "tests": tests,
    "total": len(tests),
    "passed": passed,
    "failed": len(tests) - passed,
    "overall_status": "passed" if tests and passed == len(tests) else "failed",
}

with open("report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))
