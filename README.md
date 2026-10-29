# Assignment Submission Portal with Automated Testing

CSC418 DevOps - Lab Midterm Examination
Student: Husnain | Registration No.: FA23-BSE-003/ATK
Repository: [REPO_URL] | Pages URL (bonus): [PAGES_URL]

## 1. What This Project Does

A small Flask web portal where students enter their name, registration number, assignment title and a submission URL. The portal validates the input, saves valid submissions to a JSON file and lists them on the page.

Every push to GitHub starts a CI pipeline (GitHub Actions) that:

1. runs the automated tests,
2. builds a JSON report from the real test results,
3. sends the report to a receiver running on your own computer, which saves it as `test-report.json`,
4. optionally emails the report (bonus), and
5. deploys the static demo to GitHub Pages only if all tests passed on `main` (bonus).

## 2. Project Structure

```
app/                      Flask application
  app.py                  routes: list (GET /) and submit (POST /submit)
  validation.py           required-field and URL validation
  templates/index.html    page template
tests/
  conftest.py             test client fixture (uses a temporary storage file)
  test_submissions.py     the 3 required test cases
receiver/receiver.py      local HTTP receiver, writes test-report.json
scripts/build_report.py   converts pytest results.xml into report.json
scripts/send_email.py     bonus: emails the report over SMTP
docs/index.html           bonus: static demo published to GitHub Pages
.github/workflows/ci.yml  CI pipeline
evidence/                 screenshots for the submission (see evidence/README.txt)
CSC418_Lab_Midterm_Submission.docx   submission document template
```

## 3. Prerequisites

| Tool | Purpose | Check with |
|------|---------|------------|
| Python 3.10 or newer | run app, tests, receiver | `python --version` |
| Git | version control | `git --version` |
| GitHub account | repository and Actions | - |
| cloudflared or ngrok | tunnel from GitHub to your computer | `cloudflared --version` or `ngrok version` |

On Windows, use PowerShell or Git Bash. If `python` is not found, try `py`.

## 4. Run the Application Locally

```bash
python -m venv .venv
# Windows PowerShell:  .venv\Scripts\Activate.ps1
# Windows cmd:         .venv\Scripts\activate.bat
# macOS / Linux:       source .venv/bin/activate
pip install -r requirements.txt
python -m app.app
```

Open http://127.0.0.1:5000. Fill in the form and submit.

- A valid submission is saved to `submissions.json` and shown in the table.
- A missing field or a URL that does not start with `http://` or `https://` shows a validation message and is not saved.

Take screenshots 01 and 02 here (see section 12).

## 5. Run the Tests

```bash
python -m pytest -v
```

Expected output: 3 passed.

| Test | Scenario | Expected result |
|------|----------|-----------------|
| `test_valid_submission_is_saved_and_listed` | all fields and a valid URL | HTTP 200, submission appears in the list |
| `test_missing_registration_number_is_rejected` | empty registration number | HTTP 400, message "Registration number is required", nothing saved |
| `test_invalid_url_is_rejected_and_not_saved` | URL `not-a-valid-url` | HTTP 400, message "Submission URL is invalid", nothing saved |

Tests use a temporary file, so they never touch your real `submissions.json`.

## 6. Start the Local Receiver

The receiver listens for the CI report and saves it as `test-report.json` in the folder where you start it.

```bash
python receiver/receiver.py
```

It prints `listening on 0.0.0.0:5001`. Keep this terminal open for the whole demonstration.

Optional environment variables: `PORT` (default 5001) and `REPORT_FILE` (default `test-report.json`).

Check it works locally, in a second terminal:

```bash
python -m pytest --junitxml=results.xml
python scripts/build_report.py
curl -X POST -H "Content-Type: application/json" --data @report.json http://localhost:5001/report
```

Windows PowerShell: use `curl.exe` instead of `curl`. The receiver prints a "saved" line and `test-report.json` appears with the test results.

## 7. Connect GitHub to Your Computer (Tunnel)

A GitHub-hosted runner cannot reach your `localhost`, so you expose the receiver through a tunnel. With the receiver running, open a second terminal:

```bash
cloudflared tunnel --url http://localhost:5001
```

or, with ngrok (after adding your auth token once):

```bash
ngrok http 5001
```

Copy the public URL it prints (for cloudflared it looks like `https://something.trycloudflare.com`). Your receiver URL is that address plus a path, for example:

```
https://something.trycloudflare.com/report
```

Test it from any terminal:

```bash
curl -X POST -H "Content-Type: application/json" -d "{\"test\": true}" https://something.trycloudflare.com/report
```

Notes:
- Keep the receiver and the tunnel running during the demo.
- Free tunnel URLs change every time you restart the tunnel. Update the `RECEIVER_URL` secret each time.

## 8. Create the GitHub Repository and Push

1. On GitHub, create a new **public** repository (Pages needs a public repo on free accounts). Do not add a README there.
2. In the project folder:

```bash
git init
git add .
git commit -m "Initial commit: portal, tests, CI, receiver"
git branch -M main
git remote add origin https://github.com/<USER>/<REPO>.git
git push -u origin main
```

Do not push yet if you want the first run to be a demo run. Set the secrets first (next section).

## 9. Configure Repository Secrets

GitHub repository, Settings, Secrets and variables, Actions, New repository secret.

| Secret | Required | Value |
|--------|----------|-------|
| `RECEIVER_URL` | yes | the full tunnel URL including `/report` |
| `EMAIL_TO` | bonus | address that receives the report |
| `SMTP_HOST` | bonus | e.g. `smtp.gmail.com` |
| `SMTP_USER` | bonus | the sending address |
| `SMTP_PASSWORD` | bonus | an app password, not your normal password |

Gmail: enable 2-step verification, then create an App Password in your Google account security settings and use it as `SMTP_PASSWORD`. The script connects over SSL on port 465.

Never commit passwords or put them in files. The pipeline reads them only from secrets.

## 10. How the CI Pipeline Works

File: `.github/workflows/ci.yml`. Trigger: every push.

Job `test`:
1. Check out the code and install Python 3.12.
2. Install dependencies.
3. Run pytest and write `results.xml` (`continue-on-error` so later steps still run).
4. Build `report.json` from `results.xml`.
5. POST `report.json` to `RECEIVER_URL` (runs for passing and failing runs).
6. Send the email if `EMAIL_TO` is set (bonus).
7. If the tests failed, fail the job, so a failing test turns the run red.

Job `deploy` (bonus): runs only on `main` and only if the `test` job succeeded. It publishes `docs/` to GitHub Pages. If tests fail, this job is skipped and the previously published site stays unchanged.

### Report format

```json
{
  "repository": "user/repo",
  "branch": "main",
  "commit_sha": "<full sha>",
  "run_id": "<github run id>",
  "timestamp": "<UTC ISO time>",
  "tests": [
    { "name": "test_name", "result": "passed", "failure_message": null }
  ],
  "total": 3,
  "passed": 3,
  "failed": 0,
  "overall_status": "passed"
}
```

## 11. Demonstration Workflow

Before starting: receiver running, tunnel running, `RECEIVER_URL` secret updated. Delete any old `test-report.json` so the change is visible.

### Run 1: passing

```bash
git commit --allow-empty -m "Demo run 1: passing"
git push
```

Open the repository's Actions tab, wait for the green run. Open `test-report.json` locally: `"overall_status": "passed"`.

### Run 2: introduce a defect (failing)

This removes the registration number from the required fields.

Git Bash, macOS, Linux:
```bash
sed -i 's/"reg_no", //' app/validation.py
```

Windows PowerShell:
```powershell
(Get-Content app/validation.py) -replace '"reg_no", ', '' | Set-Content app/validation.py
```

Confirm with `python -m pytest` (one test fails), then:

```bash
git commit -am "Introduce defect: skip reg_no validation"
git push
```

Expected: red run in Actions, `test-report.json` shows `"overall_status": "failed"`, failed count 1 and a failure message. The Pages deploy job is skipped.

### Run 3: fix the defect

```bash
git revert HEAD --no-edit
git push
```

Expected: green run, `test-report.json` shows `"passed"` again.

## 12. Evidence Checklist

Save screenshots in `evidence/` with these names, then insert them into `CSC418_Lab_Midterm_Submission.docx`.

| File | Content |
|------|---------|
| 01_portal_form_and_list.png | portal with a saved submission |
| 02_validation_message.png | validation error |
| 03_github_repo.png | repository with folders and README |
| 04_actions_run_list.png | Actions tab |
| 05_receiver_and_tunnel_running.png | both terminals running |
| 06_json_file_contents.png | test-report.json |
| 07_run1_pass_actions.png | passing run |
| 08_run1_pass_json.png | local JSON: passed |
| 09_run2_fail_actions.png | failing run |
| 10_run2_fail_json.png | local JSON: failed with message |
| 11_run3_fixed_actions.png | fixed run |
| 12_run3_fixed_json.png | local JSON: passed again |
| 13_pages_site.png | bonus: deployed site |
| 14_pages_deploy_skipped_on_fail.png | bonus: deploy skipped on failure |
| 15_email_pass.png | bonus: email for passing run |
| 16_email_fail.png | bonus: email for failing run |

## 13. Bonus Setup

### GitHub Pages
1. Settings, Pages, Source: **GitHub Actions**.
2. Push to `main` with passing tests.
3. The URL is `https://<USER>.github.io/<REPO>/` and also shows in the deploy job. Put it in this README and the Word document.

### Email report
1. Add the four email secrets (section 9).
2. Push. The email step runs on passing and failing runs and includes commit, branch, run id, result, counts, each test result and the JSON as an attachment.

## 14. Troubleshooting

| Problem | Likely cause and fix |
|---------|---------------------|
| Run is red but all tests passed | The "Send report" step failed: receiver or tunnel is not running, or `RECEIVER_URL` is outdated. Restart, update the secret, re-run the job. |
| `test-report.json` not updated | Receiver not running, wrong path in the secret, or the tunnel was restarted. Check the receiver terminal for log lines. |
| `curl: (22)` in the Actions log | The receiver returned an error status or the URL is wrong. Open the URL in a browser; the receiver answers GET with "receiver is running". |
| Deploy job skipped on a passing run | The push was not to `main`, or Pages source is not set to GitHub Actions. |
| Deploy permission error | Settings, Actions, General, Workflow permissions; and Pages source must be GitHub Actions. |
| No email arrives | `EMAIL_TO` not set, wrong SMTP host or an app password is needed. Read the "Email report" step log. |
| `ModuleNotFoundError: app` | Run commands from the project root. |
| `python` not found on Windows | Use `py`, or reinstall Python with "Add to PATH". |
| Port already in use | Set another port: `PORT=5002 python receiver/receiver.py` (PowerShell: `$env:PORT=5002`) and tunnel that port. |

## 15. Create the Final Zip

First complete the Word document with screenshots and placeholders replaced. Do not include `.git`, `.venv` or secrets.

macOS / Linux / Git Bash (run from the folder that contains the project folder):
```bash
zip -r CSC418_Lab_Midterm_Portal_Final.zip CSC418_Lab_Midterm_Portal -x "*/.git/*" "*/.venv/*" "*/__pycache__/*" "*/test-report.json" "*/submissions.json"
```

Windows PowerShell (delete `.venv` and `.git` from a copy first, because Compress-Archive cannot exclude folders):
```powershell
Compress-Archive -Path CSC418_Lab_Midterm_Portal -DestinationPath CSC418_Lab_Midterm_Portal_Final.zip
```

Verify: `unzip -l CSC418_Lab_Midterm_Portal_Final.zip` (Windows: `tar -tf CSC418_Lab_Midterm_Portal_Final.zip`).

## 16. Submission Checklist

- [ ] GitHub repository URL
- [ ] README (this file) with setup instructions
- [ ] Evidence of the passing, failing and corrected runs (GitHub Actions and local JSON)
- [ ] Completed Word document with screenshots
- [ ] Final zip file
- [ ] Bonus: Pages URL and email screenshots, if attempted
- [ ] No passwords or tokens anywhere in the repository
