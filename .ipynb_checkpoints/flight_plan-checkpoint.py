import os
import xml.etree.ElementTree as ET
import pandas as pd

# Define the XML namespace
namespace = {"ns": "http://aeec.aviation-ia.net/633"}

# Directory containing XML files
xml_directory = "airinc633_20250213"

# List to store all flight and waypoint data
all_flight_data = []
all_waypoints_data = []

# Loop through all XML files in the directory
for filename in os.listdir(xml_directory):
    if filename.endswith(".xml"):  # Ensure only process XML files
        file_path = os.path.join(xml_directory, filename)

        # Load and parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        ### --- Extract Flight Details --- ###
        flight_data = {
            "File Name": filename,  # Track the source file for reference
            "Flight Number": None,
            "Departure Airport": None,
            "Arrival Airport": None,
            "Aircraft Registration": None,
            "Scheduled Time of Departure": None,
            "Flight Date": None
        }

        # Extract flight number
        flight_number_element = root.find(".//ns:FlightIdentification/ns:FlightNumber", namespace)
        if flight_number_element is not None:
            airline_code = flight_number_element.get("airlineIATACode", "N/A")
            flight_number = flight_number_element.get("number", "N/A")
            flight_data["Flight Number"] = f"{airline_code}{flight_number}"

        # Extract departure and arrival airports
        flight_data["Departure Airport"] = root.find(".//ns:DepartureAirport/ns:AirportIATACode", namespace).text or "N/A"
        flight_data["Arrival Airport"] = root.find(".//ns:ArrivalAirport/ns:AirportIATACode", namespace).text or "N/A"

        # Extract aircraft registration number
        aircraft_element = root.find(".//ns:Aircraft", namespace)
        flight_data["Aircraft Registration"] = aircraft_element.get("aircraftRegistration", "N/A") if aircraft_element is not None else "N/A"

        # Extract scheduled departure time and flight date
        flight_element = root.find(".//ns:Flight", namespace)
        if flight_element is not None:
            flight_data["Scheduled Time of Departure"] = flight_element.get("scheduledTimeOfDeparture", "N/A")
            flight_data["Flight Date"] = flight_element.get("flightOriginDate", "N/A")

        # Store flight data
        all_flight_data.append(flight_data)

        ### --- Extract Waypoint Details --- ###
        for waypoint in root.findall(".//ns:Waypoints/ns:Waypoint", namespace):
            waypoint_data = {
                "File Name": filename,
                "Flight Number": flight_data["Flight Number"],
                "Waypoint Name": waypoint.get("waypointName", "N/A"),
                "Latitude": waypoint.find("ns:Coordinates", namespace).get("latitude", "N/A"),
                "Longitude": waypoint.find("ns:Coordinates", namespace).get("longitude", "N/A"),
                "Wind Direction (°)": waypoint.find("ns:SegmentWind/ns:Direction/ns:Value", namespace).text or "N/A",
                "Wind Speed (kt)": waypoint.find("ns:SegmentWind/ns:Speed/ns:Value", namespace).text or "N/A",
                "Time Over Waypoint": waypoint.find("ns:TimeOverWaypoint/ns:EstimatedTime/ns:Value", namespace).text or "N/A",
                "Fuel On Board (lb)": waypoint.find("ns:FuelOnBoard/ns:EstimatedWeight/ns:Value", namespace).text or "N/A"
            }

            # Store waypoint data
            all_waypoints_data.append(waypoint_data)

### --- Convert to DataFrames --- ###
flights_df = pd.DataFrame(all_flight_data)
waypoints_df = pd.DataFrame(all_waypoints_data)

# Remove the date prefix from "Time Over Waypoint" in the waypoints DataFrame
waypoints_df["Time Over Waypoint"] = waypoints_df["Time Over Waypoint"].str.replace(r"^\d{4}-\d{2}-\d{2}T", "", regex=True)

# Remove the date prefix from "Scheduled Time of Departure" in the flights DataFrame
flights_df["Scheduled Time of Departure"] = flights_df["Scheduled Time of Departure"].str.replace(r"^\d{4}-\d{2}-\d{2}T", "", regex=True)

# Save as CSV files for easier analysis
flights_df.to_csv("all_flights.csv", index=True)
waypoints_df.to_csv("all_waypoints.csv", index=True)

print(f"Processed {len(all_flight_data)} flight plans and {len(all_waypoints_data)} waypoints.")
print("Data saved as 'all_flights.csv' and 'all_waypoints.csv'.")
