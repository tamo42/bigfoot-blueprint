import os
import csv

def count_lines_fast(filename):
    with open(filename, 'rb') as f:
        lines = 0
        buf_size = 1024 * 1024
        read_f = f.raw.read

        buf = read_f(buf_size)
        while buf:
            lines += buf.count(b'\n')
            buf = read_f(buf_size)
        return lines

def main():
    cache_dir = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\cache\well_logs"
    tracker_path = r"c:\Users\tamo4\git\nhq-bigfoot-blueprint\02-workbench\03-wells-water-well-drillers\p2_states_tracker.md"

    state_counts = {}

    print("Counting wells...")
    for filename in os.listdir(cache_dir):
        if filename.startswith("USGWD_") and filename.endswith(".csv"):
            state_name = filename[6:-4].replace("_", " ")
            filepath = os.path.join(cache_dir, filename)
            # count lines and subtract 1 for header. If no newline at EOF, it might be off by 1, but this is close enough
            # actually let's just count newlines. Assuming typical CSV.
            lines = count_lines_fast(filepath)
            # typical CSVs have a header row
            count = max(0, lines - 1)
            state_counts[state_name] = count
            print(f"{state_name}: {count:,}")

    print("Updating markdown...")
    with open(tracker_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.strip().startswith('| **'):
            parts = line.split('|')
            if len(parts) > 4:
                state_raw = parts[1].replace('**', '').strip()
                if state_raw in state_counts:
                    formatted_count = f"{state_counts[state_raw]:,}"
                    parts[4] = f" {formatted_count} "
                    line = '|'.join(parts)
        new_lines.append(line)

    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("Done!")

if __name__ == '__main__':
    main()
