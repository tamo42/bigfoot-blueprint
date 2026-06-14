import os
import sys

# Set up paths for importing general helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'general')))
import utils
import enrich_places_general

def main():
    db_path = utils.get_db_path("ohio")
    # For backward compatibility, default to 0 Find Place queries (only cache hits) 
    # to protect the user's budget, but allow running.
    print("[*] Running Ohio Places API enrichment wrapper (Cache-only by default)...")
    enrich_places_general.enrich_state_database(db_path, "Ohio", max_queries=0)

if __name__ == "__main__":
    main()
