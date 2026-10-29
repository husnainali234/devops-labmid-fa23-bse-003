"""Input validation for the assignment submission portal."""
from urllib.parse import urlparse

REQUIRED_FIELDS = ("name", "reg_no", "title", "url")

LABELS = {
    "name": "Name",
    "reg_no": "Registration number",
    "title": "Assignment title",
    "url": "Submission URL",
}


def validate(data):
    """Return a list of validation messages. An empty list means the data is valid."""
    errors = []
    for field in REQUIRED_FIELDS:
        if not (data.get(field) or "").strip():
            errors.append(f"{LABELS[field]} is required")

    url = (data.get("url") or "").strip()
    if url:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            errors.append("Submission URL is invalid (must start with http:// or https://)")
    return errors
