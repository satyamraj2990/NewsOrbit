"""
Simple test script to demonstrate gdeltPyR functionality
"""
import gdelt

print("=" * 60)
print("Testing gdeltPyR - GDELT Data Access Tool")
print("=" * 60)
print()

# Initialize GDELT version 2 (most current, updates every 15 minutes)
print("Initializing GDELT version 2...")
gd2 = gdelt.gdelt(version=2)
print("✓ GDELT v2 initialized successfully")
print()

# Show schema information
print("Available columns for 'events' table:")
print(gd2.schema('events'))
print()

# Try pulling a small sample of data from a specific date
print("Attempting to pull data from Nov 1, 2016 (15-minute interval)...")
print("Note: This may take a moment as it fetches data from GDELT servers...")
print()

try:
    # Pull a single 15-minute interval from GDELT 2.0
    results = gd2.Search('2016 Nov 1', table='events', output='pd')
    
    if results is not None and len(results) > 0:
        print(f"✓ Successfully retrieved {len(results)} events")
        print()
        print("Sample of retrieved data (first 5 rows):")
        print(results.head())
        print()
        print(f"Data shape: {results.shape[0]} rows × {results.shape[1]} columns")
    else:
        print("No data returned. This could be due to:")
        print("- Network connectivity issues")
        print("- GDELT server availability")
        print("- No events in the specified time period")
except Exception as e:
    print(f"✗ Error occurred: {type(e).__name__}")
    print(f"  Message: {str(e)}")
    print()
    print("This is normal if you don't have internet connectivity or")
    print("if the GDELT servers are temporarily unavailable.")

print()
print("=" * 60)
print("Test completed!")
print("=" * 60)
