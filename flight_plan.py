import os
import xml.etree.ElementTree as ET
import csv
from tqdm import tqdm

folder_path = 'flight_plans'
namespace = {'ns': 'http://aeec.aviation-ia.net/633'}
output_csv = 'flight_waypoints_output.csv'

# Get all XML filenames first
xml_files = [f for f in os.listdir(folder_path) if f.endswith('.xml')]

with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # CSV header
    writer.writerow([
        "Commercial Flight Number", "Departure Date", "Departure Airport", "Departure Time",
        "Arrival Airport", "Arrival Time", "Waypoint Name", "Latitude", "Longitude",
        "Altitude (ft)", "Wind Speed (kt)", "Temperature (C)", "Fuel On Board (lb)"
    ])

    # Add tqdm progress bar
    for filename in tqdm(xml_files, desc="Processing XML files"):
        file_path = os.path.join(folder_path, filename)
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            commercial_flight = root.find('.//ns:FlightNumber/ns:CommercialFlightNumber', namespace)
            dep_date = root.find('.//ns:Flight', namespace)
            dep_airport = root.find('.//ns:DepartureAirport/ns:AirportIATACode', namespace)
            dep_time = root.find('.//ns:Flight[@scheduledTimeOfDeparture]', namespace)
            arr_airport = root.find('.//ns:ArrivalAirport/ns:AirportIATACode', namespace)
            arr_time = root.find('.//ns:FlightPlanSummary/ns:ScheduledTimeOfArrival', namespace)

            flight_number = commercial_flight.text if commercial_flight is not None else "N/A"
            dep_date_val = dep_date.attrib.get('flightOriginDate') if dep_date is not None else "N/A"
            dep_airport_val = dep_airport.text if dep_airport is not None else "N/A"
            dep_time_val = dep_time.attrib.get('scheduledTimeOfDeparture') if dep_time is not None else "N/A"
            arr_airport_val = arr_airport.text if arr_airport is not None else "N/A"
            arr_time_val = arr_time.text if arr_time is not None else "N/A"

            for wp in root.findall('.//ns:Waypoint', namespace):
                name = wp.attrib.get('waypointName', 'Unknown')
                coord = wp.find('ns:Coordinates', namespace)
                lat = coord.attrib.get('latitude') if coord is not None else 'N/A'
                lon = coord.attrib.get('longitude') if coord is not None else 'N/A'
                alt = wp.find('ns:Altitude/ns:EstimatedAltitude/ns:Value', namespace)
                altitude = int(alt.text) * 100 if alt is not None else "N/A"
                wind = wp.find('ns:SegmentWind/ns:Speed/ns:Value', namespace)
                wind_speed = wind.text if wind is not None else "N/A"
                temp = wp.find('ns:SegmentTemperature/ns:Value', namespace)
                temperature = temp.text if temp is not None else "N/A"
                fuel = wp.find('ns:FuelOnBoard/ns:EstimatedWeight/ns:Value', namespace)
                fuel_lb = fuel.text if fuel is not None else "N/A"

                writer.writerow([
                    flight_number, dep_date_val, dep_airport_val, dep_time_val,
                    arr_airport_val, arr_time_val, name, lat, lon,
                    altitude, wind_speed, temperature, fuel_lb
                ])

        except ET.ParseError as e:
            print(f" Error parsing {filename}: {e}")
