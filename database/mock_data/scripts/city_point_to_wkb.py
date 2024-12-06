import csv
from shapely.geometry import Point
from shapely.wkb import dumps

def transform_points_to_wkb(input_csv: str, output_csv: str) -> None:
    """
    Transform the POINT data in the input CSV file to WKB format and save to a new CSV file.

    Parameters:
    input_csv (str): The path to the input CSV file.
    output_csv (str): The path to the output CSV file.
    """
    with open(input_csv, 'r') as infile, open(output_csv, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            point_wkt = row['c_location']
            point = Point(map(float, point_wkt.replace('POINT(', '').replace(')', '').split()))
            row['c_location'] = dumps(point)
            writer.writerow(row)

input_csv = '../data/generated/cities.csv'
output_csv = '../data/generated/cities_wkb.csv'
transform_points_to_wkb(input_csv, output_csv)