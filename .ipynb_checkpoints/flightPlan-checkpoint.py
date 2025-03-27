import os
import xml.etree.ElementTree as ET
import pandas as pd

# Define namespace for XML parsing
namespace = {"ns": "http://aeec.aviation-ia.net/633"}

# Directory containing all XML flight plans
xml_directory = "airinc633_20250213"

# List all XML files
xml_files = [os.path.join(xml_directory, f) for f in os.listdir(xml_directory) if f.endswith(".xml")]

target_flight = "HAL7"  # Change this to filter a different flight

# List to store extracted waypoint data
waypoint_data = []

# Loop through all XML files
for file in xml_files:
    try:
        tree = ET.parse(file)
        root = tree.getroot()

        # Extract flight identifier
        flight_identifier = root.find(".//ns:FlightIdentifier", namespace)
        flight_identifier = flight_identifier.text if flight_identifier is not None else "N/A"

        # Only process if it matches the target flight
        if flight_identifier == target_flight:
            # Extract waypoints
            for waypoint in root.findall(".//ns:Waypoint", namespace):
                waypoint_name = waypoint.get("waypointName", "N/A")
                waypoint_id = waypoint.get("waypointId", "N/A")
                sequence_id = waypoint.get("sequenceId", "N/A")

                # Extract coordinates
                coord_element = waypoint.find("ns:Coordinates", namespace)
                latitude = coord_element.get("latitude") if coord_element is not None else "N/A"
                longitude = coord_element.get("longitude") if coord_element is not None else "N/A"

                # Extract fuel data
                fuel_onboard = waypoint.find(".//ns:FuelOnBoard/ns:EstimatedWeight/ns:Value", namespace)
                fuel_onboard = fuel_onboard.text if fuel_onboard is not None else "N/A"

                burn_off = waypoint.find(".//ns:BurnOff/ns:EstimatedWeight/ns:Value", namespace)
                burn_off = burn_off.text if burn_off is not None else "N/A"

                cumulated_burn_off = waypoint.find(".//ns:CumulatedBurnOff/ns:EstimatedWeight/ns:Value", namespace)
                cumulated_burn_off = cumulated_burn_off.text if cumulated_burn_off is not None else "N/A"

                # Extract estimated time over waypoint
                time_over_wp = waypoint.find(".//ns:TimeOverWaypoint/ns:EstimatedTime/ns:Value", namespace)
                time_over_wp = time_over_wp.text if time_over_wp is not None else "N/A"

                # Store extracted data
                waypoint_data.append({
                    "Flight Identifier": flight_identifier,
                    "Waypoint Name": waypoint_name,
                    "Waypoint ID": waypoint_id,
                    "Sequence ID": sequence_id,
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "Fuel On Board (lb)": fuel_onboard,
                    "Burn Off (lb)": burn_off,
                    "Cumulated Burn Off (lb)": cumulated_burn_off,
                    "Time Over Waypoint": time_over_wp,
                    "File Name": os.path.basename(file)
                })

    except Exception as e:
        print(f"Error processing {file}: {e}")

# Convert to DataFrame
df_waypoints_filtered = pd.DataFrame(waypoint_data)
print(df_waypoints_filtered)

df_waypoints_filtered.to_csv('flightPlan.csv', index=True)
