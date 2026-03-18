"""
Interactive demonstration of gdeltPyR functionality
"""
import gdelt
import sys

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_section(text):
    print(f"\n>>> {text}")
    print("-" * 70)

# Main Demo
print_header("gdeltPyR - Global Database of Events, Language, and Tone")
print("\nThis library provides access to GDELT's massive database of global events")
print("monitoring news media from 100+ languages across every country worldwide.")

# Initialize both versions
print_section("1. Initializing GDELT Versions")
print("Creating GDELT v1 instance (daily updates)...")
gd1 = gdelt.gdelt(version=1)
print("✓ GDELT v1 ready")

print("Creating GDELT v2 instance (15-minute updates)...")
gd2 = gdelt.gdelt(version=2)
print("✓ GDELT v2 ready")

# Show available tables
print_section("2. Available Data Tables")
print("GDELT v1.0 tables: events, gkg")
print("GDELT v2.0 tables: events, gkg, mentions")

# Show schema for events table
print_section("3. Events Table Schema (GDELT v2)")
schema = gd2.schema('events')
print(f"\nTotal columns: {len(schema)}")
print("\nFirst 10 columns:")
print(schema[['name', 'description']].head(10).to_string(index=False))

# Show schema for gkg table
print_section("4. GKG Table Schema (Global Knowledge Graph)")
gkg_schema = gd2.schema('gkg')
print(f"\nTotal columns: {len(gkg_schema)}")
print("\nFirst 5 columns:")
print(gkg_schema[['name', 'description']].head(5).to_string(index=False))

# Query recent data
print_section("5. Querying GDELT Data")
print("\nFetching events from November 1, 2016 (15-minute interval)...")
print("This demonstrates real-time data retrieval from GDELT servers...")

try:
    results = gd2.Search('2016 Nov 1', table='events', output='pd')
    
    if results is not None and len(results) > 0:
        print(f"\n✓ Successfully retrieved {len(results):,} events")
        
        # Show basic statistics
        print("\n--- Data Overview ---")
        print(f"Shape: {results.shape[0]:,} rows × {results.shape[1]} columns")
        print(f"Date range: {results['SQLDATE'].min()} to {results['SQLDATE'].max()}")
        
        # Show sample data
        print("\n--- Sample Events (first 3) ---")
        cols_to_show = ['SQLDATE', 'Actor1Name', 'Actor2Name', 'EventCode', 'QuadClass']
        if all(col in results.columns for col in cols_to_show):
            print(results[cols_to_show].head(3).to_string(index=False))
        
        # Show actor statistics
        if 'Actor1CountryCode' in results.columns:
            print("\n--- Top 5 Countries in Events ---")
            country_counts = results['Actor1CountryCode'].value_counts().head(5)
            for country, count in country_counts.items():
                print(f"  {country}: {count:,} events")
        
        # Show event categories
        if 'QuadClass' in results.columns:
            print("\n--- Event Categories ---")
            quad_counts = results['QuadClass'].value_counts()
            categories = {1: 'Verbal Cooperation', 2: 'Material Cooperation', 
                         3: 'Verbal Conflict', 4: 'Material Conflict'}
            for quad, count in quad_counts.items():
                cat_name = categories.get(quad, 'Unknown')
                print(f"  {cat_name}: {count:,} events")
        
    else:
        print("\n⚠ No data returned - server may be unavailable or no events in period")
        
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}: {str(e)}")
    print("This can happen if there's no internet connection or GDELT servers are busy")

# Show additional features
print_section("6. Additional Features")
print("""
gdeltPyR supports:
  • Date ranges: gd2.Search(['2016 Oct 31','2016 Nov 2'])
  • Multiple tables: table='events', 'gkg', 'mentions'
  • Different outputs: output='pd' (pandas), 'json', 'csv'
  • Coverage reports: coverage=True
  • Parallel downloads for multiple dates
  • Translation filtering (English vs translated sources)
  • Geospatial analysis with geopandas integration
""")

print_section("7. Use Cases")
print("""
Real-world applications:
  • Conflict monitoring and early warning systems
  • Media bias and coverage analysis
  • Sentiment analysis of global events
  • Geographic event pattern detection
  • Political science research
  • Journalism and investigative reporting
  • Crisis response and humanitarian aid planning
""")

print_header("Demo Complete!")
print("\nThe gdeltPyR library is now ready for your analysis needs.")
print("Visit https://linwoodc3.github.io/gdeltPyR/ for detailed documentation.")
print()
