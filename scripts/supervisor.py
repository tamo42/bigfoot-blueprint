import subprocess
import sys
import time

def run_batch():
    print("\n" + "="*50, flush=True)
    print("[SUPERVISOR] Starting new batch of 120 records...", flush=True)
    print("="*50 + "\n", flush=True)
    
    start_time = time.time()
    
    # 120 records at 1 request/sec = 120 seconds. 
    # Giving it 150 seconds allows for 30 seconds of network buffer.
    # If it hits 150 seconds, it's definitely hung on a 503 retry loop and we forcefully kill it!
    try:
        # We remove capture_output to allow the subprocess to stream directly to the terminal!
        result = subprocess.run(
            [sys.executable, "p4_enrich_reviews_gemini.py", "--limit", "120"],
            timeout=150
        )
        
        # To check if we are done, we can't read result.stdout anymore because it was streamed.
        # So we can just check the database size, or rely on p4_enrich_reviews_gemini to exit with a specific code.
        # A simpler way is to just let the script naturally run. If it finds 0 records, it completes in ~1 second.
        # Then the next batch will also complete in 1 second.
        # We can break the loop if the execution time is less than 5 seconds!
        
        # Check execution time:
        if time.time() - start_time < 5:
            print("\n[SUPERVISOR] Batch finished in under 5 seconds. Database must be fully enriched! Exiting.", flush=True)
            return False
            print("\n[SUPERVISOR] Found 0 remaining contractors. Database is fully enriched! Exiting.", flush=True)
            return False
            
        return True # Continue to next batch
        
    except subprocess.TimeoutExpired as e:
        print("\n[SUPERVISOR] WARNING: Batch timed out after 150 seconds! (Likely hung on a Google SDK 503 retry loop).", flush=True)
        print("[SUPERVISOR] Force-killing the hung batch and immediately starting the next one to seamlessly sweep up the remaining records!", flush=True)
        if e.stdout:
            try:
                print(e.stdout.decode('utf-8'), flush=True)
            except:
                pass
        return True # Continue to next batch
        
    except Exception as e:
        print(f"\n[SUPERVISOR] ERROR: Unexpected error: {e}", flush=True)
        return False

if __name__ == "__main__":
    print("[SUPERVISOR] Initializing autonomous enrichment loop...")
    while True:
        should_continue = run_batch()
        if not should_continue:
            break
        # Brief 3 second pause between batches to let the terminal breathe
        time.sleep(3)
