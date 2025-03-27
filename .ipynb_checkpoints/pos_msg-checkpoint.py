import sqlite3
import pandas as pd

# Connect to the SQLite database
db_path = "ac_pos_msg.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch a small sample of position messages for parsing
cursor.execute("SELECT content FROM pos_msg;")
sample_messages = cursor.fetchall()

# Close the connection
conn.close()

# Function to split the date-time field into separate day and time values
def extract_day_time(date_time_str):
    if len(date_time_str) == 6:  # Format: DDHHMM
        day = date_time_str[:2]  # First two characters = day
        time = date_time_str[2:4] + ":" + date_time_str[4:]  # Format time as HH:MM
    elif len(date_time_str) == 5:  # Format: DHHMM
        day = date_time_str[:1]  # First character = day
        time = date_time_str[1:3] + ":" + date_time_str[3:]  # Format time as HH:MM
    else:
        day, time = None, None  # Handle unexpected cases

    return day, time

# Function to extract flight number (remove "/AN" if present)
def extract_flight_number(flight_str):
    return flight_str.replace("/AN", "") if "/AN" in flight_str else flight_str

# Function to extract aircraft registration number from the 8th field
def extract_aircraft_registration(registration_str):
    return registration_str  # No additional processing needed, just return the value

# Extracts UTC time, ensuring a consistent HHMMSS format.
def extract_utc_time(utc_time_str):
    utc_time_str = utc_time_str.strip()  # Remove spaces

    if len(utc_time_str) < 5 or len(utc_time_str) > 6:
        return None  # Ignore invalid formats

    if len(utc_time_str) == 5:  # Edge case: missing leading zero
        utc_time_str = "0" + utc_time_str

    return f"{utc_time_str[:2]}:{utc_time_str[2:4]}:{utc_time_str[4:]}"

# Extracts numeric fuel onboard value, removing any extra suffix (e.g., '/TS180650').
def extract_fuel_onboard(fuel_str):
    if not fuel_str:  # Handle empty cases
        return None
    if "/" in fuel_str:
        return fuel_str.split("/")[0]  # Take only the part before '/'
    return fuel_str if fuel_str.isdigit() else None  # Ensure it only returns valid numbers

# Function to extract all relevant flight parameters from the 15th field
def extract_flight_parameters(position_str):
    if "," in position_str:  # Ensure the field contains multiple values
        split_values = position_str.split(",")  # Split by commas

        while len(split_values) < 10:  # Ensure at least 10 fields exist
            split_values.append(None)  # Fill missing values with None

        return {
            "Position Coordinates": split_values[0][3:] if split_values[0].startswith("POS") else split_values[0],  # 1st value, cleaned
            "Last Waypoint": split_values[1] if len(split_values) > 1 else None,  # 2nd value
            "Current UTC Time": extract_utc_time(split_values[2]) if len(split_values) > 2 else None,  # 3rd value
            "Altitude": split_values[3] if len(split_values) > 3 else None,  # 4th value
            "Go-To Waypoint": split_values[4] if len(split_values) > 4 else None,  # 5th value
            "ETA Go-To Waypoint": extract_utc_time(split_values[5]) if len(split_values) > 5 else None,  # 6th value
            "Waypoint After Go-To": split_values[6] if len(split_values) > 6 else None,  # 7th value
            "Air Temperature": split_values[7] if len(split_values) > 7 else None,  # 8th value
            "Actual Wind Speed": split_values[8] if len(split_values) > 8 else None,  # 9th value
            "Fuel Onboard": extract_fuel_onboard(split_values[9]) if len(split_values) > 9 else None  # 10th value
        }
    return {
        "Position Coordinates": None,
        "Last Waypoint": None,
        "Current UTC Time": None,
        "Altitude": None,
        "Go-To Waypoint": None,
        "ETA Go-To Waypoint": None,
        "Waypoint After Go-To": None,
        "Air Temperature": None,
        "Actual Wind Speed": None,
        "Fuel Onboard": None
    }

# Process each sample message by splitting on whitespace
split_messages = [msg[0].split() for msg in sample_messages]

# Display the split results
for i, msg in enumerate(split_messages):
    print(f"Message {i+1} Split:\n", msg, "\n")

# Apply function to the 4th field (date-time field) in each message
extracted_dates_times = [extract_day_time(msg[3]) for msg in split_messages]

# Apply function to the 7th field (flight number field) in each message
extracted_flight_numbers = [extract_flight_number(msg[6]) for msg in split_messages]

# Apply function to the 8th field (aircraft registration) in each message
extracted_aircraft_registrations = [extract_aircraft_registration(msg[7]) for msg in split_messages]

# Apply function to extract flight parameters from the 15th field
extracted_flight_params = [extract_flight_parameters(msg[14]) for msg in split_messages]

# Combine the extracted values with the original messages
formatted_messages = [
    {"Day": extracted_dates_times[i][0],
     "Time": extracted_dates_times[i][1],
     "Flight Number":extracted_flight_numbers[i],
     "Aircraft Registration": extracted_aircraft_registrations[i],
     "Position Coordinates": extracted_flight_params[i]["Position Coordinates"],
     "Last Waypoint": extracted_flight_params[i]["Last Waypoint"],
     "Current UTC Time": extracted_flight_params[i]["Current UTC Time"],
     "Altitude": extracted_flight_params[i]["Altitude"],
     "Go-To Waypoint": extracted_flight_params[i]["Go-To Waypoint"],
     "ETA Go-To Waypoint": extracted_flight_params[i]["ETA Go-To Waypoint"],
     "Waypoint After Go-To": extracted_flight_params[i]["Waypoint After Go-To"],
     "Actual Wind Speed": extracted_flight_params[i]["Actual Wind Speed"],
     "Air Temperature": extracted_flight_params[i]["Air Temperature"],
     "Fuel Onboard": extracted_flight_params[i]["Fuel Onboard"]
     }
    for i, msg in enumerate(split_messages)
]

# Display results
df = pd.DataFrame(formatted_messages)
print(df)

# Filter by a specific flight
def filter_by_flight(df, flight_number):
    return df[df["Flight Number"] == flight_number]

flight_to_filter = "HA7"  # Change this to the flight number you want to filter
df_filtered = filter_by_flight(df, flight_to_filter)
# Sort by Current UTC Time
df_filtered_sorted = df_filtered.sort_values(by="Current UTC Time")
print(df_filtered_sorted)

# Save to CSV
df.fillna("N/A", inplace=True)
df.to_csv('pos_msg.csv', index=True)
df_filtered_sorted.to_csv('pos_msg_filtered_sorted.csv', index=True)
