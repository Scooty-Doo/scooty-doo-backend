import csv

def generate_zone_types(output_file: str) -> None:
    """
    Generates a CSV file with zone type data.
    """
    zone_types = [
        {
            "id": 1,
            "type_name": "Parking",
            "speed_limit": 0,
            "start_fee": 5,
            "end_fee": 5,
        },
        {
            "id": 2,
            "type_name": "Charging",
            "speed_limit": 0,
            "start_fee": 0,
            "end_fee": 0,
        },
        {
            "id": 3,
            "type_name": "Forbidden",
            "speed_limit": 0,
            "start_fee": 5,
            "end_fee": 20,
        },
        {
            "id": 4,
            "type_name": "Slow",
            "speed_limit": 10,
            "start_fee": 10,
            "end_fee": 10,
        },
    ]

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["id", "type_name", "speed_limit", "start_fee", "end_fee"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for zone_type in zone_types:
            writer.writerow(zone_type)


def generate_zones(output_file: str) -> None:
    """
    Generate zones and save them to a CSV file.

    Parameters:
    output_file (str): The file path to save the generated CSV file.
    """
    zones = [
        {
            "zone_name": "Malmö C",
            "zone_type_id": 1,
            "city_id": 3,
            "boundary": "POLYGON((12.999047 55.60899, 12.999326 55.608445, 12.999219 55.608439, 12.99895 55.608984, 12.999047 55.60899))",
        },
        {
            "zone_name": "Möllevångstorget",
            "zone_type_id": 2,
            "city_id": 3,
            "boundary": "POLYGON((13.008059 55.59143, 13.008059 55.591518, 13.008478 55.591518, 13.008478 55.59143, 13.008059 55.59143))",
        },
        {
            "zone_name": "Triangeln Nord",
            "zone_type_id": 2,
            "city_id": 3,
            "boundary": "POLYGON((13.000329 55.594031, 13.000329 55.594225, 13.000581 55.594225, 13.000581 55.594031, 13.000329 55.594031))",
        },
        {
            "zone_name": "Stora pildammen",
            "zone_type_id": 3,
            "city_id": 3,
            "boundary": "POLYGON((12.998543 55.58732, 12.997727 55.589502, 12.996268 55.590036, 12.997084 55.591491, 12.994809 55.59183, 12.99232 55.590933, 12.994294 55.590206, 12.99365 55.589624, 12.996011 55.587756, 12.998114 55.587198, 12.998543 55.58732))",
        },
        {
            "zone_name": "Folkets park",
            "zone_type_id": 4,
            "city_id": 3,
            "boundary": "POLYGON((13.013241 55.595153, 13.013842 55.59525, 13.01573 55.594377, 13.014615 55.591733, 13.01204 55.592049, 13.011954 55.592364, 13.013241 55.595153))",
        },
    ]

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["zone_name", "zone_type_id", "city_id", "boundary"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for zone in zones:
            writer.writerow(zone)

output_file_path = "../data/generated/zone_types.csv"
generate_zone_types(output_file_path)
output_file_path = "../data/generated/zones.csv"
generate_zones(output_file_path)