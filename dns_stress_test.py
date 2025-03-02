import concurrent.futures
import time
import random
import dnsresolver

DOMAINS = [
    "google.com",  # Valid domain
    "facebook.com",  # Valid domain
    "nonexistentdomain.xyz",  # Non-existent domain
    "example.invalid",  # Invalid TLD
    "slowwebsite.example",  # Simulating a slow response (replace with an actual slow domain)
    "198.41.0.4",  # Testing direct root server query
]

def stress_test(mode, domain):
    """Performs a single DNS lookup in iterative or recursive mode."""
    start_time = time.time()
    if mode == "iterative":
        dnsresolver.iterative_dns_lookup(domain)
    else:
        dnsresolver.recursive_dns_lookup(domain)
    elapsed = time.time() - start_time
    print(f"[STRESS TEST] {mode.upper()} {domain} completed in {elapsed:.3f} seconds")

def run_stress_test(mode, num_requests=50):
    """Executes multiple DNS lookups in parallel to simulate high load."""
    print(f"[STARTING STRESS TEST] Mode: {mode.upper()}, Requests: {num_requests}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for _ in range(num_requests):
            domain = random.choice(DOMAINS)
            futures.append(executor.submit(stress_test, mode, domain))

        concurrent.futures.wait(futures)

    print("[STRESS TEST COMPLETE]")

if __name__ == "__main__":
    run_stress_test("iterative",50)  # Test iterative resolver with 50 queries
    run_stress_test("recursive", 50)  # Test recursive resolver with 50 queries
