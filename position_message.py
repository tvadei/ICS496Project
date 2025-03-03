import sqlite3
import pandas as pd

# Connect to SQLite database
db_path = "ac_pos_msg.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query the pos_msg table
cursor.execute("SELECT content FROM pos_msg")
rows = cursor.fetchall()

# List to store structured data
structured_data = []

# Process each row
for row in rows:
    content = row[0]  # Extract content
    split_content = content.split()  # Split by spaces

    if len(split_content) == 15:
        del split_content[13]  # Remove 14th element (index 13)

    # Modify the 7th element (index 6) if it contains "/AN"
    if "/AN" in split_content[6]:
        split_content[6] = split_content[6].replace("/AN", "")  # Remove "/AN"

    # Extract the 14th element (now at index 13) and split it by commas
    if len(split_content) > 13:
        expanded_elements = split_content[13].split(",")  # Split by commas
        split_content = split_content[:13] + expanded_elements  # Insert expanded elements

    # Remove "POS" from the new 14th element if it starts with "POS"
    if len(split_content) > 13 and split_content[13].startswith("POS"):
        split_content[13] = split_content[13][3:]  # Remove first 3 characters ("POS")

    # Extract day of the month and time from the 4th element (index 3)
    if len(split_content) > 3 and len(split_content[3]) == 6:
        day_of_month = split_content[3][:2]  # First 2 characters
        time_hhmm = split_content[3][2:]  # Last 4 characters
        split_content[3] = day_of_month  # Replace with extracted day
        split_content.insert(4, time_hhmm)  # Insert extracted time after day

    # Split the 24th element (now at index 23) by "/"
    if len(split_content) > 23 and "/" in split_content[23]:
        split_24th = split_content[23].split("/")  # Split by slash
        split_content = split_content[:23] + split_24th + split_content[24:]  # Insert the split parts

    # Ensure the list has exactly 25 elements
    while len(split_content) < 25:
        split_content.append(None)  # Fill missing values with None
    if len(split_content) > 25:
        split_content = split_content[:25]  # Trim any unexpected excess elements

    # Map structured data
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
df.to_csv("cleaned_position_message.csv", index=True)

conn.close()
