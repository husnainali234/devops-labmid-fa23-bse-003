VALID = {
    "name": "Test Student",
    "reg_no": "FA00-XXX-000/ATK",
    "title": "Midterm Lab",
    "url": "https://github.com/example/repo",
}


def test_valid_submission_is_saved_and_listed(client):
    response = client.post("/submit", data=VALID, follow_redirects=True)
    assert response.status_code == 200
    page = client.get("/").data
    assert b"Midterm Lab" in page
    assert b"https://github.com/example/repo" in page


def test_missing_registration_number_is_rejected(client):
    data = {**VALID, "reg_no": ""}
    response = client.post("/submit", data=data)
    assert response.status_code == 400
    assert b"Registration number is required" in response.data
    assert b"Midterm Lab" not in client.get("/").data


def test_invalid_url_is_rejected_and_not_saved(client):
    data = {**VALID, "url": "not-a-valid-url"}
    response = client.post("/submit", data=data)
    assert response.status_code == 400
    assert b"Submission URL is invalid" in response.data
    assert b"not-a-valid-url" not in client.get("/").data
