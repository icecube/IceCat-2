import numpy as np

'''
file1 = "evts_without_scan_28Jan.txt"
file2 = "scans_completed_28Jan.txt"

run1, evt1 = np.loadtxt(file1, usecols=(0,1), unpack=True, dtype=int)
run2, evt2 = np.loadtxt(file2, usecols=(0,1), unpack=True, dtype=int)

print("Number of events with scan completed = ", len(run2))
print("Number of events without scan        = ", len(run1))
print("                                sum  = ", len(run1)+len(run2))
'''

def compare_files(file1, file2):
    def read_file(filename):
        with open(filename, "r") as f:
            return {tuple(line.strip().split()[:2]) for line in f}

    # Read first two columns of both files into sets
    set1 = read_file(file1)
    set2 = read_file(file2)

    # Count elements
    print(f"{file1} contains {len(set1)} unique elements (first two columns).")
    print(f"{file2} contains {len(set2)} unique elements (first two columns).")

    # Find missing lines
    missing_in_file2 = set1 - set2
    missing_in_file1 = set2 - set1

    # Print results
    if missing_in_file2:
        print(f"\nLines in {file1} but missing in {file2}:")
        for line in missing_in_file2:
            print("\t", *line)

    if missing_in_file1:
        print(f"\nLines in {file2} but missing in {file1}:")
        for line in missing_in_file1:
            print("\t", *line)

    if not missing_in_file1 and not missing_in_file2:
        print("\nBoth files contain the same first two columns.")

compare_files("../docs/division_LED_HED_old_events.txt", "../docs/scans_completed_old_evts.txt")
compare_files("../docs/division_LED_HED_i3live_events.txt", "../docs/scans_completed_i3live_evts.txt")
