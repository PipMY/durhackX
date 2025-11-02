# src/co2_calculator.py

def calculate_co2(travel_hours: float) -> float:
    """
    Estimates CO2 emissions in kg for a given travel duration in hours.
    This is a simplified model.

    Args:
        travel_hours (float): The duration of the travel in hours.

    Returns:
        float: Estimated CO2 emissions in kilograms.
    """
    if travel_hours <= 0:
        return 0.0

    # Based on https://www.eurostar.com/uk-en/sustainability/co2-calculator
    # and other sources, short-haul flights are roughly 150-250 g CO2e/pax-km.
    # A flight from London to Paris (350km) is ~1.2 hours. CO2 is ~50kg.
    # So, kg_co2_per_hour is roughly 50 / 1.2 = 41.6
    # Let's use a simple linear model for this mock.
    # CO2 (kg) = travel_hours * factor
    
    KG_CO2_PER_HOUR = 45.0 

    # Add some non-linearity: longer flights are often more efficient per hour
    if travel_hours > 8:
        factor = KG_CO2_PER_HOUR * 0.85
    elif travel_hours < 2:
        factor = KG_CO2_PER_HOUR * 1.1
    else:
        factor = KG_CO2_PER_HOUR

    return travel_hours * factor
