import json
import random
import time

import requests


def randomize_coordinates(geojson_file: str, num_coordinates: int) -> list[tuple]:
    """
    Randomize one of the features in the GeoJSON file and note the longitude and latitude
    for the first coordinate of the object.

    Parameters:
    geojson_file (str): The path to the GeoJSON file.
    num_coordinates (int): The number of coordinates to note.

    Returns:
    list: A list of tuples representing the coordinates (longitude, latitude).
    """
    with open(geojson_file) as f:
        data = json.load(f)

    coordinates_list = []

    for _ in range(num_coordinates):
        first_feature = random.choice(data["features"])
        first_coordinate = first_feature["geometry"]["coordinates"][0]
        first_long, first_lat = first_coordinate[0], first_coordinate[1]
        second_feature = random.choice(data["features"])
        second_coordinate = second_feature["geometry"]["coordinates"][0]
        second_long, second_lat = second_coordinate[0], second_coordinate[1]
        coordinates_list.append(((first_long, first_lat), (second_long, second_lat)))

    return coordinates_list


def get_bike_routes(coordinate_tuples: list) -> list:
    """
    Get bike routes from OSRM API for a list of coordinate tuples.

    Parameters:
    coordinate_tuples (list): A list of tuples representing the coordinates (longitude, latitude).

    Returns:
    list: A list of responses from the OSRM API.
    """
    base_url = "https://router.project-osrm.org/route/v1/bike/"
    responses = []

    for coord_pair in coordinate_tuples:
        coord_str = f"{coord_pair[0][0]},{coord_pair[0][1]};{coord_pair[1][0]},{coord_pair[1][1]}"
        url = f"{base_url}{coord_str}?overview=full"

        response = requests.get(url)
        if response.status_code == 200:
            responses.append(response.json())
        else:
            print(
                f"Request failed with status code {response.status_code} \
                for coordinates {coord_str}"
            )

        time.sleep(1)

    return responses


def save_responses_to_json(responses: list, output_file: str) -> None:
    """
    Save the responses to a JSON file.

    Parameters:
    responses (list): A list of responses from the OSRM API.
    output_file (str): The path to the output JSON file.
    """
    with open(output_file, "w") as f:
        json.dump(responses, f, indent=4)


geojson_file = "../data/source/map_data/malmo_bike_paths.geojson"
# Ändra till antal rutter att skapa (VAR SÄKER PÅ ATT INTE BRYTA MOT API-ANVÄNDNINGSREGLER)
num_coordinates = 500
coordinates = randomize_coordinates(geojson_file, num_coordinates)
print(coordinates)
responses = get_bike_routes(coordinates)
print(responses)
# Ändra till korrekt output-fil
save_responses_to_json(responses, "../data/source/routes/malmo_routes.json")
