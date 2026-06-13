import os
import sys
import socket
import urllib.request
import urllib.error
import json
import argparse
from datetime import datetime

# Standard WHOIS servers for common TLDs
WHOIS_SERVERS = {
    "com": "whois.verisign-grs.com",
    "net": "whois.verisign-grs.com",
    "org": "whois.pir.org",
    "info": "whois.afilias.net",
    "biz": "whois.neulevel.biz",
    "us": "whois.neustar.us",
    "co": "whois.nic.co",
    "io": "whois.nic.io",
    "app": "whois.nic.google",
    "dev": "whois.nic.google"
}

def check_dns(domain):
    """Check if the domain resolves to an IP address."""
    try:
        socket.gethostbyname(domain)
        return True  # Resolves -> Taken
    except socket.gaierror:
        return False # Doesn't resolve -> Might be available

def check_rdap(domain):
    """Check availability using ICANN's Registration Data Access Protocol (RDAP)."""
    # rdap.org acts as a bootstrap redirector to the correct registry endpoint
    url = f"https://rdap.org/domain/{domain}"
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AntigravityDomainChecker/1.0'}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return "TAKEN"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "AVAILABLE"
        elif e.code == 429:
            return "RATE_LIMITED"
        else:
            return f"ERROR_{e.code}"
    except Exception as e:
        return f"ERROR_{type(e).__name__}"
    return "UNKNOWN"

def check_whois_socket(domain):
    """Perform a raw TCP query on Port 43 to the registry WHOIS server."""
    tld = domain.split(".")[-1].lower()
    server = WHOIS_SERVERS.get(tld)
    if not server:
        # Fallback query to whois.iana.org to find the correct WHOIS server
        server = "whois.iana.org"
        
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((server, 43))
        
        # Format query for IANA or registry
        query = f"{domain}\r\n"
        s.send(query.encode("utf-8"))
        
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
        s.close()
        
        res_text = response.decode("utf-8", errors="ignore").lower()
        
        # Check standard availability indicators in text
        not_found_phrases = [
            "no match for", 
            "not found", 
            "no data found", 
            "free", 
            "available", 
            "incorrect domain name",
            "no entries found"
        ]
        
        if any(phrase in res_text for phrase in not_found_phrases):
            return "AVAILABLE"
        else:
            return "TAKEN"
            
    except Exception as e:
        return f"ERROR_{type(e).__name__}"

def check_domain(domain):
    """Run sequential check stages: DNS -> RDAP -> WHOIS fallback."""
    domain = domain.strip().lower()
    if not domain or "." not in domain:
        return {"domain": domain, "status": "INVALID", "details": "Invalid domain format"}
        
    print(f"Checking {domain}...")
    
    # Stage 1: DNS Lookup (Fastest, zero cost)
    dns_resolves = check_dns(domain)
    if dns_resolves:
        return {
            "domain": domain,
            "status": "TAKEN",
            "method": "DNS Resolution",
            "details": "Resolves to active IP address"
        }
        
    # Stage 2: RDAP Registry check
    rdap_result = check_rdap(domain)
    if rdap_result == "AVAILABLE":
        return {
            "domain": domain,
            "status": "AVAILABLE",
            "method": "RDAP Protocol",
            "details": "Registry reports domain not registered (404)"
        }
    elif rdap_result == "TAKEN":
        return {
            "domain": domain,
            "status": "TAKEN",
            "method": "RDAP Protocol",
            "details": "Registry records found (200)"
        }
        
    # Stage 3: Raw WHOIS Fallback (if RDAP rate limited or erred)
    whois_result = check_whois_socket(domain)
    if whois_result == "AVAILABLE":
        return {
            "domain": domain,
            "status": "AVAILABLE",
            "method": "Port 43 WHOIS Socket",
            "details": "Registry WHOIS server returned 'No Match'"
        }
    elif whois_result == "TAKEN":
        return {
            "domain": domain,
            "status": "TAKEN",
            "method": "Port 43 WHOIS Socket",
            "details": "Registry WHOIS server contains registration details"
        }
        
    # If all else fails, output check result details
    return {
        "domain": domain,
        "status": "UNKNOWN",
        "method": "Fallback Failure",
        "details": f"RDAP: {rdap_result}, WHOIS: {whois_result}"
    }

def main():
    parser = argparse.ArgumentParser(description="Secure non-registrar domain availability checker.")
    parser.add_argument("domains", nargs="*", help="Domain names to check (e.g. check-domain.py mydomain.com mydomain.net)")
    parser.add_argument("--file", help="Path to file containing domain names (one per line)")
    
    args = parser.parse_args()
    
    domains_to_check = []
    
    if args.domains:
        domains_to_check.extend(args.domains)
        
    if args.file:
        file_path = Path(args.file)
        if file_path.exists():
            with open(file_path, "r") as f:
                domains_to_check.extend([line.strip() for line in f if line.strip() and not line.strip().startswith("#")])
        else:
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
            
    if not domains_to_check:
        # Interactive Mode
        print("--- Secure Domain Checker (Interactive Mode) ---")
        print("Enter domain names separated by spaces, or type 'exit' to quit.\n")
        while True:
            try:
                user_input = input("domains > ").strip()
                if user_input.lower() in ("exit", "quit", "q"):
                    break
                if not user_input:
                    continue
                
                for d in user_input.split():
                    result = check_domain(d)
                    status_color = "\033[92mAVAILABLE\033[0m" if result['status'] == "AVAILABLE" else "\033[91mTAKEN\033[0m" if result['status'] == "TAKEN" else "\033[93mUNKNOWN\033[0m"
                    print(f"  Verdict: {status_color} (via {result['method']}: {result['details']})")
                print()
            except (KeyboardInterrupt, EOFError):
                break
        return

    # Batch output formatting
    print("\n" + "="*85)
    print(f"{'DOMAIN NAME':<30} | {'VERDICT':<12} | {'CHECK METHOD':<20} | {'DETAILS'}")
    print("="*85)
    
    available_count = 0
    
    for d in domains_to_check:
        res = check_domain(d)
        
        # Clean print format
        verdict = res["status"]
        method = res.get("method", "N/A")
        details = res.get("details", "")
        
        print(f"{d:<30} | {verdict:<12} | {method:<20} | {details}")
        if verdict == "AVAILABLE":
            available_count += 1
            
    print("="*85)
    print(f"Completed checking {len(domains_to_check)} domains. {available_count} available for purchase.\n")

if __name__ == "__main__":
    main()
