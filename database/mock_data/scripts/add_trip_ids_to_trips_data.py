import csv


def add_ids_to_trips():
    """Add incrementing IDs to trip data CSV."""
    input_file = '../data/generated/trip_data.csv'
    output_file = '../data/generated/trip_data_with_ids.csv'
    
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Get header and add id column
        header = next(reader)
        writer.writerow(['id'] + header)
        
        # Add rows with incrementing ids
        for i, row in enumerate(reader, 1):
            writer.writerow([i] + row)

if __name__ == "__main__":
    add_ids_to_trips()