import ipaddress
import socket
from urllib.parse import urlparse


def is_safe_url(url: str) -> bool:
    """
    Check if a URL is safe to crawl.
    Blocks localhost, private IPs, and non-http(s) schemes (SSRF protection).
    """
    try:
        parsed = urlparse(url)

        # Only allow http and https
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Block obvious localhost names
        blocked_names = ("localhost", "127.0.0.1", "0.0.0.0", "::1")
        if hostname.lower() in blocked_names:
            return False

        # Resolve the hostname to an IP and check if it's private/internal
        try:
            ip_str = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_str)
            # Block private, loopback, link-local, and reserved IPs
            if (ip.is_private or ip.is_loopback or
                    ip.is_link_local or ip.is_reserved or ip.is_multicast):
                return False
        except (socket.gaierror, ValueError):
            # If we can't resolve the hostname, treat it as unsafe
            return False

        return True

    except Exception:
        return False