import gdelt
print("Initializing GDELT...")
gd = gdelt.gdelt(version=2)
print("Fetching data...")
results = gd.Search('2016 Nov 1', table='events')
print(f"SUCCESS! Retrieved {len(results)} events from GDELT database")
print(f"First event: {results.iloc[0]['Actor1Name']} -> {results.iloc[0]['Actor2Name']}")
