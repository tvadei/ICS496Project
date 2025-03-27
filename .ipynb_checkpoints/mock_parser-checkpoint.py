import os
import xml.etree.ElementTree as ET
import pandas as pd

## Parsing the XML files

namespace = {"ns": "http://aeec.aviation-ia.net/633"}

xml_directory = "airinc633_20250213"

all_flight_data = []
all_waypoints_data = []

for filename in os.listdir(xml_directory):
    if filename.endswith(".xml"):
        file_path = os.path.join(xml_directory, filename)

        tree = ET.parse(file_path)
        root = tree.getroot()

        flight_data = {
            "File Name": filename,
            "Flight Number": None,
            "Departure Airport": None,
            "Arrival Airport": None,
            "Aircraft Registration": None,
            "Scheduled Time of Departure": None,
            "Flight Date": None
        }

        flight_number_element = root.find(".//ns:FlightIdentification/ns:FlightNumber", namespace)
        if flight_number_element is not None:
            airline_code = flight_number_element.get("airlineIATACode", "N/A")
            flight_number = flight_number_element.get("number", "N/A")
            flight_data["Flight Number"] = f"{airline_code}{flight_number}"

        flight_data["Departure Airport"] = root.find(".//ns:DepartureAirport/ns:AirportIATACode", namespace).text or "N/A"
        flight_data["Arrival Airport"] = root.find(".//ns:ArrivalAirport/ns:AirportIATACode", namespace).text or "N/A"

        aircraft_element = root.find(".//ns:Aircraft", namespace)
        flight_data["Aircraft Registration"] = aircraft_element.get("aircraftRegistration", "N/A") if aircraft_element is not None else "N/A"

        flight_element = root.find(".//ns:Flight", namespace)
        if flight_element is not None:
            flight_data["Scheduled Time of Departure"] = flight_element.get("scheduledTimeOfDeparture", "N/A")
            flight_data["Flight Date"] = flight_element.get("flightOriginDate", "N/A")

        all_flight_data.append(flight_data)

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

            all_waypoints_data.append(waypoint_data)

flights_df = pd.DataFrame(all_flight_data)
waypoints_df = pd.DataFrame(all_waypoints_data)

waypoints_df["Time Over Waypoint"] = waypoints_df["Time Over Waypoint"].str.replace(r"^\d{4}-\d{2}-\d{2}T", "", regex=True)

flights_df["Scheduled Time of Departure"] = flights_df["Scheduled Time of Departure"].str.replace(r"^\d{4}-\d{2}-\d{2}T", "", regex=True)

flights_df.to_csv("all_flights.csv", index=True)
waypoints_df.to_csv("all_waypoints.csv", index=True)

print(f"Processed {len(all_flight_data)} flight plans and {len(all_waypoints_data)} waypoints.")
print("Data saved as 'all_flights.csv' and 'all_waypoints.csv'.")

#-------------------#

import sqlite3

db_path = "ac_pos_msg.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT content FROM pos_msg")
rows = cursor.fetchall()

structured_data = []

for row in rows:
    content = row[0]
    split_content = content.split()

    if len(split_content) == 15:
        del split_content[13]

    if "/AN" in split_content[6]:
        split_content[6] = split_content[6].replace("/AN", "")


    if len(split_content) > 13:
        expanded_elements = split_content[13].split(",")
        split_content = split_content[:13] + expanded_elements

    if len(split_content) > 13 and split_content[13].startswith("POS"):
        split_content[13] = split_content[13][3:]

    if len(split_content) > 3 and len(split_content[3]) == 6:
        day_of_month = split_content[3][:2]
        time_hhmm = split_content[3][2:]
        split_content[3] = day_of_month
        split_content.insert(4, time_hhmm)

    if len(split_content) > 23 and "/" in split_content[23]:
        split_24th = split_content[23].split("/")
        split_content = split_content[:23] + split_24th + split_content[24:]


    while len(split_content) < 25:
        split_content.append(None)
    if len(split_content) > 25:
        split_content = split_content[:25]


    structured_entry = {
        "Day": split_content[3] if len(split_content) > 3 else None,
        "Time_HHMM": split_content[4] if len(split_content) > 4 else None,
        "Flight_Number": split_content[7] if len(split_content) > 7 else None,
        "Aircraft_Registration": split_content[8] if len(split_content) > 8 else None,
        "Position_LatLon": split_content[14] if len(split_content) > 14 else None,
        "Last_Waypoint": split_content[15] if len(split_content) > 15 else None,
        "Current_UTC_Time": split_content[16] if len(split_content) > 16 else None,
        "Altitude": split_content[17] if len(split_content) > 17 else None,
        "GOTO_Waypoint": split_content[18] if len(split_content) > 18 else None,
        "ETA_GOTO": split_content[19] if len(split_content) > 19 else None,
        "GOTO+1_Waypoint": split_content[20] if len(split_content) > 20 else None,
        "Air_Temperature": split_content[21] if len(split_content) > 21 else None,
        "Actual_Wind": split_content[22] if len(split_content) > 22 else None,
        "Fuel_Onboard": split_content[23] if len(split_content) > 23 else None,
        "Current_UTC_Time_Duplicate": split_content[24] if len(split_content) > 24 else None
    }

    structured_data.append(structured_entry)

df = pd.DataFrame(structured_data)

print(df.head(10))

df.insert(0, "Index", range(1, len(df) + 1))
df.to_csv("position_messages.csv", index=True)

conn.close()

#---- Some Basic Analysis ---#

# Filter only for flight "HA1641"
ha1641_df = df[df["Flight_Number"] == "HA1641"]

# Convert "Time_HHMM" to ensure proper sorting (handling it as string for now)
ha1641_df = ha1641_df.sort_values(by="Time_HHMM", ascending=True)

# Save filtered results
ha1641_df.to_csv("position_messages_HA1641.csv", index=False)

# Display the first 10 rows for verification
print("\nPosition Messages for HA1641:")
print(ha1641_df.head(10))

# Filter waypoints for flight "HA1641"
ha1641_waypoints_df = waypoints_df[waypoints_df["Flight Number"] == "HA1641"]

# Convert "Time Over Waypoint" to ensure proper sorting
ha1641_waypoints_df["Time Over Waypoint"] = pd.to_datetime(ha1641_waypoints_df["Time Over Waypoint"], format="%H:%M:%S").dt.time

# Group by "File Name" (same flight plan) and sort each group by "Time Over Waypoint"
ha1641_waypoints_df = ha1641_waypoints_df.sort_values(by=["File Name", "Time Over Waypoint"], ascending=[True, True])

# Save the grouped and sorted waypoints to a CSV file
ha1641_waypoints_df.to_csv("waypoints_HA1641.csv", index=False)

# Display the first 10 grouped waypoints
print("\nWaypoints for HA1641 (Grouped by File Name):")
print(ha1641_waypoints_df.head(10))

