import polars as pl

if __name__ == "__main__":
    # in your code, copy the files to your local environment and update the paths accordingly
    schedule_files = "data/raw/[0-9]*.csv"
    emissions_file = "data/raw/emissions.csv"

    # read in csv files using polars
    schedules = pl.scan_csv(schedule_files, infer_schema_length=10000)
    emissions = pl.scan_csv(emissions_file, infer_schema_length=10000)
    
    print(schedules)
    print(emissions)
    
    # information on the columns in the data files can be found at:
    # https://knowledge.oag.com/docs/wdf-record-layout
    # https://knowledge.oag.com/docs/emissions-schedules-data-fields-explained
    
    # filter for flights from London (LHR) to Mumbai (BOM)
    london_to_mumbai_flights = (
        schedules.filter((pl.col("DEPAPT") == "LHR") & (pl.col("ARRAPT") == "BOM"))
    )
    
    print("London to Mumbai Flights:")
    print(london_to_mumbai_flights.collect())
    
    # Join with the emissions data on carrier and flight number, sorting on emissions
    result = (
        london_to_mumbai_flights.join(
            emissions,
            left_on=["CARRIER", "FLTNO"],
            right_on=["CARRIER_CODE", "FLIGHT_NUMBER"],
            how="inner"
        )
        .sort("ESTIMATED_CO2_TOTAL_TONNES")
        .select([
            pl.col("FLTNO"),
            pl.col("DEPAPT"),
            pl.col("ARRAPT"),
            pl.col("ELPTIM"),
            pl.col("ESTIMATED_CO2_TOTAL_TONNES")
        ])
    ).collect()
    
    # print the chosen columns
    print("London to Mumbai Flights By Emissions:")
    print(result)
    