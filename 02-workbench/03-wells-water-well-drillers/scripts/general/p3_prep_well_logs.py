import os
import csv
import json
from collections import defaultdict

def create_county_stats():
    """
    Parses all state CSVs from the USGWD dataset and generates a lightweight JSON cache
    of average well depth and yield per county for the last 10 years.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cache_dir = os.path.join(base_dir, "cache", "well_logs")
    output_file = os.path.join(cache_dir, "county_groundwater_stats.json")

    # Structure: stats[state][county] = {total_depth, count_depth, total_yield, count_yield, total_wells}
    stats = defaultdict(lambda: defaultdict(lambda: {
        'total_depth': 0.0,
        'count_depth': 0,
        'total_yield': 0.0,
        'count_yield': 0,
        'total_wells': 0
    }))

    if not os.path.exists(cache_dir):
        print(f"[-] Error: Cache directory not found at {cache_dir}")
        return

    csv_files = [f for f in os.listdir(cache_dir) if f.startswith("USGWD_") and f.endswith(".csv")]
    if not csv_files:
        print("[-] No USGWD CSV files found in cache.")
        return

    print(f"[+] Found {len(csv_files)} state dataset files. Processing...")

    for filename in csv_files:
        filepath = os.path.join(cache_dir, filename)
        print(f"  -> Parsing {filename}...")
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    state = row.get('State', '').strip().upper()
                    county = row.get('County', '').strip().upper()
                    
                    if not state or not county:
                        continue

                    # Filter for last 10 years (dataset ends around 2024, so >= 2014)
                    year_str = row.get('Year Well was Constructed', '')
                    if not year_str:
                        continue
                    try:
                        year = int(float(year_str))
                        if year < 2014:
                            continue
                    except ValueError:
                        continue

                    # Parse Depth
                    depth_str = row.get('Well Depth (Feet)', '')
                    depth_val = None
                    if depth_str:
                        try:
                            depth_val = float(depth_str)
                        except ValueError:
                            pass

                    # Parse Yield
                    yield_str = row.get('Well Capacity (GPM)', '')
                    yield_val = None
                    if yield_str:
                        try:
                            yield_val = float(yield_str)
                        except ValueError:
                            pass

                    # Update Accumulators
                    stats[state][county]['total_wells'] += 1
                    
                    if depth_val is not None and depth_val > 0:
                        stats[state][county]['total_depth'] += depth_val
                        stats[state][county]['count_depth'] += 1
                        
                    if yield_val is not None and yield_val > 0:
                        stats[state][county]['total_yield'] += yield_val
                        stats[state][county]['count_yield'] += 1
        except Exception as e:
            print(f"  [!] Error parsing {filename}: {e}")

    # Finalize Averages
    print("\n[+] Calculating county averages...")
    final_stats = {}
    
    for state, counties in stats.items():
        final_stats[state] = {}
        for county, data in counties.items():
            avg_depth = None
            if data['count_depth'] > 0:
                avg_depth = round(data['total_depth'] / data['count_depth'])
                
            avg_yield = None
            if data['count_yield'] > 0:
                avg_yield = round(data['total_yield'] / data['count_yield'])
                
            final_stats[state][county] = {
                'avg_depth_ft': avg_depth,
                'avg_yield_gpm': avg_yield,
                'recent_wells_count': data['total_wells']
            }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_stats, f, indent=2)

    print(f"\n[+] Success! Wrote optimized stats for {len(final_stats)} states to {output_file}")

if __name__ == "__main__":
    create_county_stats()
