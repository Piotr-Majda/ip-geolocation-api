import pytest

from app.interfaces.api.routes.v1.geolocation_router import domain_validator


@pytest.mark.parametrize(
    "value,expected",
    [
        ("www.google.com:8080", "google.com"),
        ("http://www.google.com", "google.com"),
        ("https://www.google.com", "google.com"),
        ("www.google.com", "google.com"),
        ("sub.domain.co.uk", "domain.co.uk"),
        ("example.org", "example.org"),
        ("my-site123.net", "my-site123.net"),
    ],
)
def test_domain_validator_valid(value, expected):
    result = domain_validator(value)
    assert result == expected, f"Expected {expected}, got {result}"


@pytest.mark.parametrize(
    "value",
    [
        "google",  # no dot
        pytest.param(
            "www.google", marks=pytest.mark.xfail(reason="tldextract limitation: not a valid TLD")
        ),
        pytest.param(
            "http://www.google",
            marks=pytest.mark.xfail(reason="tldextract limitation: not a valid TLD"),
        ),
        "ftp://notadomain",  # not a valid domain
        "http://localhost",  # no TLD after extraction
        "",
        None,
        123,
    ],
)
def test_domain_validator_invalid(value):
    try:
        result = domain_validator(value)
        pytest.fail(
            f"FAILED: domain_validator({value!r}) != '{result}' did NOT raise an exception!"
        )
    except (ValueError, TypeError):
        pass  # Test passes if exception is raised
