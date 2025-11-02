import csv
import os
from datetime import datetime, timedelta

def find_best_flight(departure_airport, arrival_airport, arrival_datetime_str, leeway_hours=0):
    """
    Finds the best flight based on the desired arrival time, prioritizing the previous day if needed.

    Returns:
        dict: Contains only departure_time, arrival_time, duration, and price, or None.
    """
    try:
        target_datetime = datetime.fromisoformat(arrival_datetime_str.replace('Z', '+00:00'))
    except ValueError:
        print("Error: Invalid datetime format. Please use ISO format like 'YYYY-MM-DDTHH:MM:SSZ'.")
        return None

    latest_arrival_datetime = target_datetime - timedelta(hours=leeway_hours)

    def flight_info(flight):
        dep = flight.get('SCHEDULED_DEPARTURE_DATE_TIME_UTC')
        arr = flight.get('SCHEDULED_ARRIVAL_DATE_TIME_UTC')
        duration = _calculate_duration_utc(dep, arr)
        price = _estimate_price(duration)
        return {
            'departure_time': dep,
            'arrival_time': arr,
            'duration': duration,
            'price': price
        }

    # Use year, month, day from latest_arrival_datetime
    year = latest_arrival_datetime.year
    month = latest_arrival_datetime.month
    day = latest_arrival_datetime.day

    flights_before_target = _search_file(departure_airport, arrival_airport, year, month, day, max_arrival_datetime=latest_arrival_datetime)
    if flights_before_target:
        best = max(flights_before_target, key=lambda x: x.get('SCHEDULED_ARRIVAL_DATE_TIME_UTC', ''))
        return flight_info(best)

    previous_day_dt = latest_arrival_datetime - timedelta(days=1)
    flights_on_previous_day = _search_file(departure_airport, arrival_airport, previous_day_dt.year, previous_day_dt.month, previous_day_dt.day)
    if flights_on_previous_day:
        best = max(flights_on_previous_day, key=lambda x: x.get('SCHEDULED_ARRIVAL_DATE_TIME_UTC', ''))
        return flight_info(best)

    all_flights_on_day = _search_file(departure_airport, arrival_airport, year, month, day, max_arrival_datetime=latest_arrival_datetime)
    if all_flights_on_day:
        best = min(all_flights_on_day, key=lambda x: x.get('SCHEDULED_ARRIVAL_DATE_TIME_UTC', ''))
        return flight_info(best)

    return None

def _search_file(departure_airport, arrival_airport, year, month, day, max_arrival_datetime=None):
    """Helper function to search a single day's flight data in data/2024/{month}/{day}.csv."""
    flights = []
    file_name = f"{day:02d}.csv"
    file_path = os.path.join('data', str(year), f"{month:02d}", file_name)

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('DEPAPT') == departure_airport and row.get('ARRAPT') == arrival_airport:
                    if max_arrival_datetime:
                        arrival_utc_str = row.get('SCHEDULED_ARRIVAL_DATE_TIME_UTC')
                        if arrival_utc_str:
                            try:
                                # Handle potential timezone info at the end of the string
                                if '.' in arrival_utc_str:
                                    arrival_utc_str = arrival_utc_str.split('.')[0]
                                arrival_dt = datetime.fromisoformat(arrival_utc_str)
                                if arrival_dt <= max_arrival_datetime.replace(tzinfo=None):
                                    flights.append(row)
                            except (ValueError, TypeError):
                                continue # Ignore rows with bad date formats
                    else:
                        flights.append(row)
    except Exception:
        # Ignoring file read errors for this broader search
        pass
    
    return flights

def _estimate_price(duration_minutes):
    """Estimates the price of a flight in GBP based on its duration."""
    if duration_minutes <= 0:
        return 0
    # Simple model: base fare + price per minute
    base_fare = 40  # A constant base fare in GBP
    price_per_minute = 0.65 # A multiplier for the duration in GBP
    
    # Add some variability to make it look more realistic
    # For example, longer flights might have a slightly lower per-minute cost
    if duration_minutes > 300: # 5 hours
        price_per_minute = 0.5
    elif duration_minutes < 90: # 1.5 hours
        price_per_minute = 0.8

    estimated_price = base_fare + (duration_minutes * price_per_minute)
    
    # Let's add a small random factor to make it less deterministic for the same duration
    import random
    estimated_price *= random.uniform(0.95, 1.05)

    return round(estimated_price, 2)

def _calculate_duration_utc(departure_utc_str, arrival_utc_str):
    """Calculates flight duration in minutes from UTC datetime strings."""
    if not departure_utc_str or not arrival_utc_str:
        return 0
    try:
        dep_dt = datetime.fromisoformat(departure_utc_str)
        arr_dt = datetime.fromisoformat(arrival_utc_str)
        duration = (arr_dt - dep_dt).total_seconds() / 60
        return int(duration)
    except (ValueError, TypeError):
        return 0 # Return 0 if formats are invalid

# if __name__ == '__main__':
#     # Example usage:
#     arrival_datetime = "2024-06-22T12:00:00Z"
#     depart_airport = "LHR"
#     arrive_airport = "LAX"
#     leeway = 3 # 3 hours of leeway
    
#     best_flight = find_best_flight(depart_airport, arrive_airport, arrival_datetime, leeway_hours=leeway)
    
#     if best_flight:
#         print(f"Best flight found from {depart_airport} to {arrive_airport} near {arrival_datetime} with at least {leeway} hours leeway:")
#         print(f"Departure: {best_flight['departure_time']}")
#         print(f"Arrival: {best_flight['arrival_time']}")
#         print(f"Duration: {best_flight['duration']} mins")
#         print(f"Estimated Price: £{best_flight['price']}")
#     else:
#         print(f"No flights found from {depart_airport} to {arrive_airport} near {arrival_datetime} with the specified leeway.")

#     best_flight = find_best_flight("LHR", "CDG", "2024-06-15T12:00:00Z", leeway_hours=3)
#     print(best_flight)