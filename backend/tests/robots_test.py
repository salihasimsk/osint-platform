from app.crawler.robots import can_crawl

sites = [
    "https://nvd.nist.gov/vuln",
    "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
    "https://ubuntu.com/security/notices",
    "https://access.redhat.com/security/security-updates/",
    "https://www.kb.cert.org/vuls/",
]

for site in sites:
    if can_crawl(site):
        print(f"✅ Taranabilir: {site}")
    else:
        print(f"❌ Yasak: {site}")
