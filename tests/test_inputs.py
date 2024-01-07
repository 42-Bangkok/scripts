from app.services.inputs import get_logins


def test_get_logins():
    users = get_logins("app/inputs/tutor_experience_reset.csv.sample")
    assert users == ["sample-user-545697cc-1b3e", "sample-user-545697cc-7d4b"]
