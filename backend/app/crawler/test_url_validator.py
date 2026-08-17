import socket

import pytest

from app.crawler.url_validator import is_safe_url


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost",
        "http://127.0.0.1",
        "http://10.0.0.1",
        "http://192.168.1.10",
        "http://169.254.169.254",
        "http://[::1]",
    ],
)
def test_blocks_local_and_private_urls(url):
    assert is_safe_url(url) is False


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.com/file",
        "javascript:alert(1)",
    ],
)
def test_blocks_unsafe_schemes(url):
    assert is_safe_url(url) is False


def test_blocks_urls_with_credentials():
    url = "https://user:password@example.com"

    assert is_safe_url(url) is False


def test_allows_public_ip():
    assert is_safe_url("https://8.8.8.8") is True


def test_blocks_hostname_resolving_to_private_ip(
    monkeypatch,
):
    def fake_getaddrinfo(*args, **kwargs):
        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("10.0.0.5", 0),
            )
        ]

    monkeypatch.setattr(
        "app.crawler.url_validator.socket.getaddrinfo",
        fake_getaddrinfo,
    )

    assert is_safe_url("https://example.com") is False


def test_allows_hostname_resolving_to_public_ip(
    monkeypatch,
):
    def fake_getaddrinfo(*args, **kwargs):
        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("8.8.8.8", 0),
            )
        ]

    monkeypatch.setattr(
        "app.crawler.url_validator.socket.getaddrinfo",
        fake_getaddrinfo,
    )

    assert is_safe_url("https://example.com") is True
