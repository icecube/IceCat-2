import re
import csv

# Regular expressions to capture each piece of data
run_eventid_pattern = re.compile(r"Run = (\d+), EventID = (\d+)")
error_region_pattern = re.compile(r"RA = ([\d\.-]+) \+ ([\d\.-]+) - ([\d\.-]+)\s+Dec = ([\d\.-]+) \+ ([\d\.-]+) - ([\d\.-]+)")
contour_area_pattern = re.compile(r"Contour Area \(50%\): ([\d\.-]+) square degrees")
contour_area_90_pattern = re.compile(r"Contour Area \(90%\): ([\d\.-]+) square degrees")
saving_pattern = re.compile(r"Saving contour to (.+)")

# Function to extract data from the file
def extract_info_from_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    
    # Split the content into blocks of data
    entries = text.split("Saving")  # Assuming entries are separated by a blank line
    
    results = []
    
    for entry in entries:
        # Extracting run and event ID
        run_eventid_match = re.search(run_eventid_pattern, entry)
        if run_eventid_match:
            run = run_eventid_match.group(1)
            event_id = run_eventid_match.group(2)
        else:
            run, event_id = None, None
        
        # Extracting 50% and 90% error region for RA and Dec
        error_region_match = re.search(error_region_pattern, entry)
        if error_region_match:
            ra_50 = error_region_match.group(1)
            ra_50_min = error_region_match.group(2)
            ra_50_max = error_region_match.group(3)
            
            dec_50 = error_region_match.group(4)
            dec_50_min = error_region_match.group(5)
            dec_50_max = error_region_match.group(6)
        else:
            ra_50, ra_50_min, ra_50_max = None, None, None
            dec_50, dec_50_min, dec_50_max = None, None, None
        
        # Extracting 90% error region for RA and Dec
        ra_90_match = re.search(r"RA = ([\d\.-]+) \+ ([\d\.-]+) - ([\d\.-]+)\s+Dec = ([\d\.-]+) \+ ([\d\.-]+) - ([\d\.-]+)", entry)
        if ra_90_match:
            ra_90 = ra_90_match.group(1)
            ra_90_min = ra_90_match.group(2)
            ra_90_max = ra_90_match.group(3)
            
            dec_90 = ra_90_match.group(4)
            dec_90_min = ra_90_match.group(5)
            dec_90_max = ra_90_match.group(6)
        else:
            ra_90, ra_90_min, ra_90_max = None, None, None
            dec_90, dec_90_min, dec_90_max = None, None, None
        
        # Extracting contour areas
        contour_area_match = re.search(contour_area_pattern, entry)
        contour_area_90_match = re.search(contour_area_90_pattern, entry)
        if contour_area_match and contour_area_90_match:
            contour_area_50 = contour_area_match.group(1)
            contour_area_90 = contour_area_90_match.group(1)
        else:
            contour_area_50, contour_area_90 = None, None
        
        # Extracting saving path
        saving_match = re.search(saving_pattern, entry)
        if saving_match:
            saving_path = saving_match.group(1)
        else:
            saving_path = None
        
        results.append({
            'Run': run,
            'EventID': event_id,
            'RA': ra_50,
            'Dec': dec_50,
            'RA_50_min': ra_50_min,
            'RA_50_max': ra_50_max,
            'Dec_50_min': dec_50_min,
            'Dec_50_max': dec_50_max,
            'RA_90_min': ra_90_min,
            'RA_90_max': ra_90_max,
            'Dec_90_min': dec_90_min,
            'Dec_90_max': dec_90_max,
            'Contour Area (50%)': contour_area_50,
            'Contour Area (90%)': contour_area_90
        })
    
    return results

# Function to save the extracted info to a CSV file
def save_to_csv(data, output_file):
    # Fieldnames for the CSV file (keys from the dictionary)
    fieldnames = ['Run', 'EventID', 'RA', 'Dec', 'RA_50_min', 'RA_50_max', 'Dec_50_min', 'Dec_50_max',
                  'RA_90_min', 'RA_90_max', 'Dec_90_min', 'Dec_90_max', 
                  'Contour Area (50%)', 'Contour Area (90%)']
    
    # Open the CSV file in write mode
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header (column names)
        writer.writeheader()
        
        # Write the data (rows)
        for row in data:
            writer.writerow(row)

file_path = 'output_reco.txt'
output_file = 'output_reco.csv'
extracted_info = extract_info_from_file(file_path)
save_to_csv(extracted_info, output_file)
print(f"Data saved to {output_file}")

