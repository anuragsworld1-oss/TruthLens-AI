"""
TruthLens AI - Source Intelligence & SSRF-Protected Web Extraction Engine
Extracts full article content, domain, publisher metadata, author, and timestamp.
Implements strict Server-Side Request Forgery (SSRF) filters preventing queries
to internal networks, localhost, link-local, and AWS/cloud metadata services.
"""

import socket
import ipaddress
import urllib.parse
import trafilatura
from bs4 import BeautifulSoup
import requests

# Documented domain registry for transparency
DOCUMENTED_PUBLISHERS = {
    "reuters.com": {"name": "Reuters", "type": "Global News Agency / Wire", "established": "1851", "rating": "High Transparency & Editorial Verification"},
    "apnews.com": {"name": "Associated Press", "type": "Global News Cooperative / Wire", "established": "1846", "rating": "High Transparency & Editorial Verification"},
    "bbc.com": {"name": "BBC News", "type": "Public Broadcaster", "established": "1922", "rating": "High Transparency & Editorial Verification"},
    "nature.com": {"name": "Nature Portfolio", "type": "Peer-Reviewed Scientific Journal", "established": "1869", "rating": "Peer-Reviewed Academic Rigor"},
    "nasa.gov": {"name": "NASA Official Portal", "type": "Government Space Agency", "established": "1958", "rating": "Official Scientific Authority"},
    "who.int": {"name": "World Health Organization", "type": "United Nations Specialized Health Agency", "established": "1948", "rating": "Official Health Authority"},
    "isro.gov.in": {"name": "ISRO Official Portal", "type": "Government Space Agency", "established": "1969", "rating": "Official Scientific Authority"},
    "thehindu.com": {"name": "The Hindu", "type": "National Daily Newspaper", "established": "1878", "rating": "Established Print & Digital Journalism"},
    "pib.gov.in": {"name": "Press Information Bureau (PIB)", "type": "Government Information Disseminator", "established": "1919", "rating": "Official Government Press Agency"}
}

def is_safe_url(url: str) -> tuple[bool, str]:
    """
    Validates URL scheme and resolves hostname to ensure it does not route
    to private networks, loopbacks, link-local, multicast, or cloud metadata endpoints.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False, "Unsupported URL scheme. Only HTTP and HTTPS are permitted."

        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL hostname."

        # Disallow localhost alias directly
        if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            return False, "Access to localhost and internal loopback addresses is prohibited."

        # Check for IP literal in hostname directly
        try:
            ip_obj = ipaddress.ip_address(hostname)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
                return False, f"URL points to restricted private/internal address ({hostname})."
        except ValueError:
            # Hostname is a domain name, not an IP literal
            pass

        # Resolve IP addresses for the hostname
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                ip_obj = ipaddress.ip_address(ip_str)

                # Block private networks, loopbacks, link-local (e.g. AWS 169.254.169.254)
                if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
                    return False, f"URL resolves to restricted private/internal network address ({ip_str})."
        except socket.gaierror:
            # Offline or sandboxed DNS resolution environment: check that domain has valid public TLD
            parts = hostname.split(".")
            if len(parts) >= 2 and parts[-1].isalpha() and len(parts[-1]) >= 2:
                return True, "URL hostname format is valid (offline resolution)."
            return False, f"Cannot resolve hostname '{hostname}' and format is invalid."

        return True, "URL is safe for extraction."
    except Exception as e:
        return False, f"URL validation failed: {str(e)}"

def extract_article_from_url(url: str) -> dict:
    """
    Safely extracts article text, metadata, publisher details, author, and date.
    """
    safe, msg = is_safe_url(url)
    if not safe:
        raise ValueError(msg)

    parsed = urllib.parse.urlparse(url)
    domain = parsed.hostname.lower() if parsed.hostname else ""
    if domain.startswith("www."):
        domain = domain[4:]

    # Fetch webpage safely with custom headers and timeout
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 TruthLens/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True, stream=True)
    resp.raise_for_status()

    # Enforce maximum response size (5MB) to prevent memory exhaustion attacks
    content_chunks = []
    total_bytes = 0
    for chunk in resp.iter_content(chunk_size=16384):
        total_bytes += len(chunk)
        if total_bytes > 5 * 1024 * 1024:
            raise ValueError("Target webpage exceeds maximum permissible download size (5MB).")
        content_chunks.append(chunk)

    html_text = b"".join(content_chunks).decode(resp.encoding or "utf-8", errors="replace")

    # Extract clean article body using trafilatura
    extracted_text = trafilatura.extract(html_text, include_comments=False, include_tables=False)
    
    # Metadata extraction using BeautifulSoup
    soup = BeautifulSoup(html_text, "html.parser")
    
    # Title extraction
    title = ""
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()
    elif soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Author extraction
    author = "Unknown"
    author_meta = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", property="article:author")
    if author_meta and author_meta.get("content"):
        author = author_meta["content"].strip()

    # Date extraction
    pub_date = "Not specified"
    date_meta = soup.find("meta", property="article:published_time") or soup.find("meta", attrs={"name": "publication_date"})
    if date_meta and date_meta.get("content"):
        pub_date = date_meta["content"].strip()[:10]

    # Publisher intelligence
    publisher_info = DOCUMENTED_PUBLISHERS.get(domain, {
        "name": domain.title(),
        "type": "General Web Publisher",
        "established": "Unrecorded in local registry",
        "rating": "Unclassified (New or Independent Domain)"
    })

    if not extracted_text:
        # Fallback to paragraph joining if trafilatura extraction found no body
        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 30]
        extracted_text = "\n\n".join(paragraphs)

    return {
        "title": title or "Untitled Article",
        "text": extracted_text or "",
        "author": author,
        "published_at": pub_date,
        "domain": domain,
        "canonical_url": url,
        "publisher_intelligence": publisher_info
    }
