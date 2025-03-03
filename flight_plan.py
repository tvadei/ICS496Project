import xml.etree.ElementTree as ET
import pandas as pd

# Define the XML namespace
namespace = {"ns": "http://aeec.aviation-ia.net/633"}

# Load and parse the XML file
file_path = "airinc633_20250213/202502130005502333080.xml"
tree = ET.parse(file_path)
root = tree.getroot()

### --- Extract Flight Details --- ###
flight_info = {}

# Extract flight number
flight_number_element = root.find(".//ns:FlightIdentification/ns:FlightNumber", namespace)
if flight_number_element is not None:
    airline_code = flight_number_element.get("airlineIATACode", "N/A")
    flight_number = flight_number_element.get("number", "N/A")
    flight_info["Flight Number"] = f"{airline_code}{flight_number}"

# Extract departure and destination airports
departure_element = root.find(".//ns:DepartureAirport/ns:AirportICAOCode", namespace)
arrival_element = root.find(".//ns:ArrivalAirport/ns:AirportICAOCode", namespace)

flight_info["Departure Airport"] = departure_element.text if departure_element is not None else "N/A"
flight_info["Arrival Airport"] = arrival_element.text if arrival_element is not None else "N/A"

# Extract aircraft registration number
aircraft_element = root.find(".//ns:Aircraft", namespace)
flight_info["Aircraft Registration"] = aircraft_element.get("aircraftRegistration", "N/A") if aircraft_element is not None else "N/A"

# Extract scheduled time of departure
departure_time_element = root.find(".//ns:Flight", namespace)
flight_info["Scheduled Time of Departure"] = departure_time_element.get("scheduledTimeOfDeparture", "N/A") if departure_time_element is not None else "N/A"

# Extract flight date
flight_info["Flight Date"] = departure_time_element.get("flightOriginDate", "N/A") if departure_time_element is not None else "N/A"

# Print flight details
print("\nFlight Details:")
for key, value in flight_info.items():
    print(f"{key}: {value}")

### --- Extract Waypoint Details --- ###
waypoints_data = []

for waypoint in root.findall(".//ns:Waypoints/ns:Waypoint", namespace):
    waypoint_name = waypoint.get("waypointName", "N/A")

    # Extract coordinates
    coordinates_element = waypoint.find("ns:Coordinates", namespace)
    latitude = coordinates_element.get("latitude", "N/A") if coordinates_element is not None else "N/A"
    longitude = coordinates_element.get("longitude", "N/A") if coordinates_element is not None else "N/A"

    # Extract wind direction and speed
    wind_direction_element = waypoint.find("ns:SegmentWind/ns:Direction/ns:Value", namespace)
    wind_speed_element = waypoint.find("ns:SegmentWind/ns:Speed/ns:Value", namespace)
    wind_direction = wind_direction_element.text if wind_direction_element is not None else "N/A"
    wind_speed = wind_speed_element.text if wind_speed_element is not None else "N/A"

    # Extract time over waypoint
    time_over_element = waypoint.find("ns:TimeOverWaypoint/ns:EstimatedTime/ns:Value", namespace)
    time_over_waypoint = time_over_element.text if time_over_element is not None else "N/A"

    # Extract fuel on board
    fuel_element = waypoint.find("ns:FuelOnBoard/ns:EstimatedWeight/ns:Value", namespace)
    fuel_on_board = fuel_element.text if fuel_element is not None else "N/A"

    # Append to list
    waypoints_data.append([waypoint_name, latitude, longitude, wind_direction, wind_speed, time_over_waypoint, fuel_on_board])

# Convert to DataFrame for better visualization
waypoints_df = pd.DataFrame(waypoints_data, columns=["Waypoint Name", "Latitude", "Longitude", "Wind Direction (°)", "Wind Speed (kt)", "Time Over Waypoint", "Fuel On Board (lb)"])

# Print waypoints data as a table
print("\nWaypoint Details:")
print(waypoints_df.to_string(index=False))
