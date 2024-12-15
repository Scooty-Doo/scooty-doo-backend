import csv
import random
def add_availability_to_bikes():
    input_file = '../data/generated/bikes.csv'
    output_file = '../data/generated/bikes_with_availability.csv'
    
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['is_available']
        
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            row['is_available'] = str(random.choice(['true', 'false'])).lower()
            writer.writerow(row)

if __name__ == "__main__":
    add_availability_to_bikes()