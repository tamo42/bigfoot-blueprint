import re

def main():
    log_file = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\03-WELLS_Scout_Log.md"
    tracker_file = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\p2_states_tracker.md"

    # 1. Parse Scout Log for states with Bulk/API
    bulk_states = set()
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        blocks = content.split('## State: ')
        for block in blocks[1:]:
            lines = block.strip().split('\n')
            state = lines[0].strip()
            for line in lines[1:]:
                if line.startswith('- **Method Found**:'):
                    if 'Bulk' in line or 'API' in line:
                        bulk_states.add(state)
                    break

    print(f"States with Bulk/API: {bulk_states}")

    # 2. Parse Tracker for well counts
    state_counts = {}
    with open(tracker_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('| **'):
                parts = line.split('|')
                if len(parts) > 4:
                    state = parts[1].replace('**', '').strip()
                    count_str = parts[4].strip().replace(',', '')
                    if count_str.isdigit():
                        state_counts[state] = int(count_str)

    # 3. Filter and Sort
    valid_states = [(s, state_counts.get(s, 0)) for s in bulk_states if s in state_counts]
    valid_states.sort(key=lambda x: x[1], reverse=True)

    print("\nTop Tier 2 Candidates (Bulk/API + Highest Wells):")
    for s, c in valid_states:
        print(f"{s}: {c:,}")

if __name__ == '__main__':
    main()
