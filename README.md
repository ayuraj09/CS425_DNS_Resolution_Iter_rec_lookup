# DNS Resolver Assignment   

This implements a DNS resolution system that supports both iterative and recursive lookups.

## Key Features

- **Iterative DNS Resolution:** Queries root servers, then TLD servers, and finally authoritative servers to resolve a domain name step by step, without relying on intermediate resolvers.
- **Recursive DNS Resolution:** Delegates the entire resolution process to a recursive resolver, which contacts multiple servers as needed and returns the final resolved IP address.
- **Graceful Error Handling:** Handles errors like non-existent domains, timeouts, and no-answer responses.
- **Efficiency:** Uses a timeout mechanism and fallback methods to improve resolution.

## Important Functions and Definitions

1. **`send_dns_query(server, domain)`**
   - Sends a DNS query to the specified nameserver for an A record.
   - Returns the response if successful, otherwise `None`.

2. **`resolve_ns_name(ns_name)`**
   - Uses the system resolver to fetch A records for a nameserver hostname.
   - Returns a list of resolved IP addresses.

3. **`extract_next_nameservers(response)`**
   - Extracts NS records from the authority section and tries to resolve their A records.
   - Uses additional section first and falls back to system resolver if necessary.

4. **`iterative_dns_lookup(domain)`**
   - Starts from the root DNS servers and follows a step-by-step resolution process.
   - Queries each level (Root → TLD → Authoritative) until an answer is found.
   - **In simple terms:** The resolver asks one server at a time, moving step by step down the hierarchy until it finds the answer.

5. **`recursive_dns_lookup(domain)`**
   - Uses `dns.resolver.resolve()` to perform a full recursive resolution.
   - Fetches and displays the final resolved IP address.
   - **In simple terms:** The resolver delegates the query to another resolver, which does all the work by querying different servers and returns the final result.

6. **`timeout`**
    - The DNS queries have a **timeout of 3 seconds** per attempt to ensure responsiveness and avoid long delays.


## Correctness

The implementation follows the correct DNS resolution procedures:
- Both modes correctly handle failure cases, including NXDOMAIN and timeout scenarios.
- The number of IP addresses returned for a domain varies based on its DNS configuration:
  - Some domains return a **single IP** if they only have one A record.
  - Others return **multiple IPs** due to load balancing, redundancy, or CDN configurations.
  - `example.com`, for instance, is hosted on **Akamai's CDN**, which returns multiple IPs dynamically.

## Stress Testing

Stress testing was conducted to evaluate the resolver’s performance under high query loads. Multiple DNS queries were executed in parallel using Python’s `ThreadPoolExecutor`, simulating concurrent client requests. The test included valid, invalid, and slow-responding domains to assess the resolver’s efficiency, response times, and robustness under varying conditions. The results helped identify performance bottlenecks and optimize timeout handling.

## Limitations

- **Iterative resolution may fail for some domains:** Some domains rely on intermediate resolvers and do not return enough information for manual traversal.
- **Network dependency:** Responses may vary based on network conditions, server availability, and DNS policies.
- **Limited root server list:** Only a subset of root DNS servers is included for querying.
- **Variable response behavior:** The number of returned IPs may change based on resolver settings, caching, and CDN policies.

## Challenges Faced

1. **Iterative resolution failed for ****`example.com`****, but recursive mode worked correctly.**
   - **Reason:** `example.com` returns delegation responses without providing enough direct IPs in the additional section.
   - **Resolution:** Implemented a fallback mechanism to resolve NS hostnames via system resolver.
   - **Learning:** Some domains rely on intermediate resolvers, making iterative resolution challenging.

## Sources

- [RFC 1034](https://tools.ietf.org/html/rfc1034) & [RFC 1035](https://tools.ietf.org/html/rfc1035): Domain Name System specifications
- [dnspython library documentation](https://dnspython.readthedocs.io/)
- [Root DNS server list from IANA](https://www.iana.org/domains/root/servers)

### Contribution

I have completed the entire assignment on my own.
[GithubLink](https://github.com/ayuraj09/CS425_DNS_Resolution_Itr_rec_lookup)

## Declaration  
- The entire work, including server implementation and functionalities, was originally done by me.  
- All code, logic, and design were developed independently to meet the assignment requirements.  

## Feedback

- The assignment provided valuable hands-on experience with DNS querying and network programming.
- Implementing iterative resolution was particularly challenging due to the complexities of real-world DNS delegation.
- Understanding DNS response structures and handling edge cases improved debugging and problem-solving skills.
- This project deepened understanding of DNS resolution and network protocols in practical scenarios.

