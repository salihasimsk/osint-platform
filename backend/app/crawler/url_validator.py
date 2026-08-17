import ipaddress
import socket
from urllib.parse import urlparse


BLOCKED_HOSTNAMES = {
    "localhost",
    "metadata.google.internal",
}

BLOCKED_SUFFIXES = (
    ".localhost",
    ".local",
    ".internal",
)


def is_safe_url(url: str) -> bool:
    """
    Return True only for public HTTP/HTTPS URLs.

    Blocks local, private, reserved and metadata addresses
    to reduce SSRF risks.
    """
    try:
        if not isinstance(url, str) or len(url) > 2048:
            return False

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        if parsed.username or parsed.password:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        hostname = hostname.rstrip(".").lower()

        if hostname in BLOCKED_HOSTNAMES:
            return False

        if hostname.endswith(BLOCKED_SUFFIXES):
            return False

        # If hostname is already an IP address, validate it directly.
        try:
            ip = ipaddress.ip_address(hostname)
            return ip.is_global
        except ValueError:
            pass

        # Resolve and validate every IPv4 and IPv6 address.
        addresses = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )

        if not addresses:
            return False

        for address in addresses:
            ip_text = address[4][0].split("%", 1)[0]
            ip = ipaddress.ip_address(ip_text)

            if not ip.is_global:
                return False

        return True

    except (
        OSError,
        ValueError,
        TypeError,
    ):
        return False
