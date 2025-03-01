import dns.message
import dns.query
import dns.rdatatype
import dns.resolver
import dns.rcode  # For checking response codes
import time

# Use A records for consistency between iterative and recursive modes
RECORD_TYPE = dns.rdatatype.A

# Root DNS servers used to start the iterative resolution process
ROOT_SERVERS = {
    "198.41.0.4": "Root (a.root-servers.net)",
    "199.9.14.201": "Root (b.root-servers.net)",
    "192.33.4.12": "Root (c.root-servers.net)",
    "199.7.91.13": "Root (d.root-servers.net)",
    "192.203.230.10": "Root (e.root-servers.net)"
}

TIMEOUT = 3  # Timeout in seconds for each DNS query attempt

def send_dns_query(server, domain):
    """ 
    Sends a DNS query to the given server for an A record of the specified domain.
    Returns the response if successful, otherwise returns None.
    """
    try:
        query = dns.message.make_query(domain, RECORD_TYPE)
        return dns.query.udp(query, server, timeout=TIMEOUT)
    except Exception:
        return None

def resolve_ns_name(ns_name):
    """
    Fallback function to resolve an NS hostname to its A records using the system resolver.
    Returns a list of IP addresses if successful, otherwise returns an empty list.
    """
    try:
        answer = dns.resolver.resolve(ns_name, "A")
        ips = [rdata.address for rdata in answer]
        print(f"Fallback: Resolved {ns_name} to {ips} using system resolver")
        return ips
    except Exception as e:
        print(f"Fallback: Unable to resolve {ns_name}: {e}")
        return []

def extract_next_nameservers(response):
    """ 
    Extracts NS records from the authority section and tries to get their A records.
    It first checks the additional section and then falls back to resolving the NS name.
    Returns a list of IPs of the next authoritative nameservers.
    """
    ns_ips = []
    ns_names = []
    
    # Extract NS records from the authority section
    for rrset in response.authority:
        if rrset.rdtype == dns.rdatatype.NS:
            for rr in rrset:
                ns_name = rr.target.to_text().rstrip('.')  # Normalize by removing trailing dot
                ns_names.append(ns_name)
                print(f"Extracted NS hostname: {ns_name}")

    # Extract A records from the additional section
    additional_a = {}
    for rrset in response.additional:
        if rrset.rdtype == dns.rdatatype.A:
            name = rrset.name.to_text().rstrip('.')  # Normalize by removing trailing dot
            a_records = [rr.address for rr in rrset]
            additional_a[name] = a_records
            print(f"Found A records for {name}: {a_records}")

    # Resolve NS hostnames using the additional records or fallback if missing
    for ns_name in ns_names:
        normalized_ns = ns_name.rstrip('.')  # Ensure no trailing dot for comparison
        if normalized_ns in additional_a:
            ns_ips.extend(additional_a[normalized_ns])
            print(f"Resolved {ns_name} to {additional_a[normalized_ns]}")
        else:
            # Fallback resolution if A record not in additional section
            fallback_ips = resolve_ns_name(ns_name)
            if fallback_ips:
                ns_ips.extend(fallback_ips)
                print(f"Resolved {ns_name} using fallback to {fallback_ips}")
            else:
                print(f"Unable to resolve NS hostname: {ns_name}")

    return ns_ips

def iterative_dns_lookup(domain):
    """ 
    Performs an iterative DNS resolution starting from root servers.
    It queries root servers, then TLD servers, then authoritative servers,
    following the hierarchy until an answer is found or a definitive error (NXDOMAIN) is returned.
    """
    print(f"[Iterative DNS Lookup] Resolving {domain}")

    next_ns_list = list(ROOT_SERVERS.keys())
    stage = "ROOT"

    while next_ns_list:
        ns_ip = next_ns_list[0]
        print(f"Querying {stage} server: {ns_ip}")
        response = send_dns_query(ns_ip, domain)
        
        if response is None:
            print(f"[ERROR] No response from {stage} server {ns_ip}, trying next server.")
            next_ns_list = next_ns_list[1:]
            continue

        # Check for error responses
        rcode = response.rcode()
        if rcode != dns.rcode.NOERROR:
            # If NXDOMAIN, it's a definitive answer that the domain does not exist.
            if rcode == dns.rcode.NXDOMAIN:
                print(f"[ERROR] NXDOMAIN: Domain '{domain}' does not exist (server {ns_ip}).")
                return
            else:
                print(f"[ERROR] DNS query to {ns_ip} returned error '{dns.rcode.to_text(rcode)}'. Trying next server.")
                next_ns_list = next_ns_list[1:]
                continue

        # If an answer is present, print it and exit.
        if response.answer:
            for rrset in response.answer:
                for rr in rrset:
                    print(f"[SUCCESS] {domain} -> {rr}")
            return
        
        # No final answer yet; extract next nameservers
        next_ns_list = extract_next_nameservers(response)
        if not next_ns_list:
            print("[ERROR] No further nameservers found. Resolution failed.")
            return

        # Update the stage for informational purposes
        if stage == "ROOT":
            stage = "TLD"
        elif stage == "TLD":
            stage = "AUTH"
        # For stages beyond AUTH, we continue using the same label.
    
    print("[ERROR] Resolution failed.")

def recursive_dns_lookup(domain):
    """ 
    Performs recursive DNS resolution using the system's default resolver.
    This approach relies on a recursive resolver (like Google DNS or a local ISP resolver)
    to fetch the result recursively.
    """
    print(f"[Recursive DNS Lookup] Resolving {domain}")
    try:
        answer = dns.resolver.resolve(domain, "A")
        for rdata in answer:
            print(f"[SUCCESS] {domain} -> {rdata}")
    except dns.resolver.NXDOMAIN:
        print(f"[ERROR] Domain '{domain}' does not exist.")
    except dns.resolver.Timeout:
        print("[ERROR] Query timed out.")
    except dns.resolver.NoAnswer:
        print(f"[ERROR] No answer found for '{domain}'.")
    except Exception as e:
        print(f"[ERROR] Recursive lookup failed: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3 or sys.argv[1] not in {"iterative", "recursive"}:
        print("Usage: python3 dnsresolver.py <iterative|recursive> <domain>")
        sys.exit(1)

    mode = sys.argv[1]
    domain = sys.argv[2]
    start_time = time.time()
    
    if mode == "iterative":
        iterative_dns_lookup(domain)
    else:
        recursive_dns_lookup(domain)
    
    print(f"Time taken: {time.time() - start_time:.3f} seconds")
