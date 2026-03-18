"""
ULTIMATE gdeltPyR DEMONSTRATION - EVERYTHING!
Shows all features, all tables, all analysis capabilities
"""
import gdelt
import pandas as pd
import json
from datetime import datetime

def banner(text):
    print("\n" + "█" * 80)
    print(f"█  {text.center(74)}  █")
    print("█" * 80)

def section(num, text):
    print(f"\n{'='*80}")
    print(f"[{num}] {text}")
    print('='*80)

banner("GDELT PyR - THE COMPLETE DEMONSTRATION")
print("\n🌍 Global Database of Events, Language, and Tone")
print("📊 Monitoring 100+ languages from every country worldwide")
print("⏱️  Updated every 15 minutes with breaking global events")

# =============================================================================
section(1, "INITIALIZE ALL VERSIONS")
# =============================================================================
print("\n🔧 Creating GDELT v1.0 instance (daily updates, historical data from 1979)...")
gd1 = gdelt.gdelt(version=1)
print("✅ GDELT v1.0 READY")

print("\n🔧 Creating GDELT v2.0 instance (15-minute updates, from Feb 2015)...")
gd2 = gdelt.gdelt(version=2)
print("✅ GDELT v2.0 READY")

# =============================================================================
section(2, "EXPLORE ALL TABLES & SCHEMAS")
# =============================================================================

tables = ['events', 'gkg', 'mentions']
print("\n📋 Available Tables:")
print("   • EVENTS: Individual events extracted from news articles")
print("   • GKG (Global Knowledge Graph): Themes, locations, people, organizations")
print("   • MENTIONS: Every mention of an event across different sources")

for table in tables[:2]:  # events and gkg
    print(f"\n📊 {table.upper()} TABLE SCHEMA:")
    schema = gd2.schema(table)
    print(f"   Total Columns: {len(schema)}")
    print(f"   Sample columns: {', '.join(schema['name'].head(5).tolist())}")

# =============================================================================
section(3, "QUERY EVENTS TABLE - Single Date")
# =============================================================================

print("\n🔍 Fetching EVENTS from November 1, 2016...")
events = gd2.Search('2016 Nov 1', table='events', output='pd')

if events is not None and len(events) > 0:
    print(f"✅ Retrieved {len(events):,} events")
    print(f"   Dimensions: {events.shape[0]:,} rows × {events.shape[1]} columns")
    
    # Time analysis
    if 'SQLDATE' in events.columns:
        print(f"\n📅 Date Coverage: {events['SQLDATE'].min()} to {events['SQLDATE'].max()}")
    
    # Actor analysis
    if 'Actor1Name' in events.columns:
        print(f"\n👥 Top 10 Actors (Actor1):")
        top_actors = events['Actor1Name'].value_counts().head(10)
        for i, (actor, count) in enumerate(top_actors.items(), 1):
            print(f"   {i:2d}. {actor:30s} → {count:4d} events")
    
    # Country analysis
    if 'Actor1CountryCode' in events.columns:
        print(f"\n🌍 Top 10 Countries:")
        countries = events['Actor1CountryCode'].value_counts().head(10)
        for i, (country, count) in enumerate(countries.items(), 1):
            print(f"   {i:2d}. {country:5s} → {count:4d} events")
    
    # Event type analysis (Goldstein Scale)
    if 'GoldsteinScale' in events.columns:
        avg_tone = events['GoldsteinScale'].mean()
        print(f"\n📈 Event Tone Analysis:")
        print(f"   Average Goldstein Score: {avg_tone:.2f}")
        print(f"   Range: {events['GoldsteinScale'].min():.1f} to {events['GoldsteinScale'].max():.1f}")
        print(f"   (Negative = conflict, Positive = cooperation)")
    
    # Quad class breakdown
    if 'QuadClass' in events.columns:
        print(f"\n🎭 Event Categories (CAMEO Quad Classes):")
        quad_map = {
            1: "Verbal Cooperation",
            2: "Material Cooperation", 
            3: "Verbal Conflict",
            4: "Material Conflict"
        }
        for quad_code in sorted(events['QuadClass'].unique()):
            count = (events['QuadClass'] == quad_code).sum()
            pct = (count / len(events)) * 100
            print(f"   {quad_map.get(quad_code, 'Unknown'):25s} → {count:4d} ({pct:5.1f}%)")
    
    # Show sample events
    print(f"\n📰 Sample Events (first 5):")
    display_cols = ['SQLDATE', 'Actor1Name', 'Actor2Name', 'EventCode', 'QuadClass', 'GoldsteinScale']
    display_cols = [col for col in display_cols if col in events.columns]
    print(events[display_cols].head(5).to_string(index=False, max_colwidth=20))

# =============================================================================
section(4, "QUERY GKG TABLE - Global Knowledge Graph")
# =============================================================================

print("\n🔍 Fetching GLOBAL KNOWLEDGE GRAPH from November 1, 2016...")
print("   (This contains themes, locations, people, organizations, tone...)")

gkg = gd2.Search('2016 Nov 1', table='gkg', output='pd')

if gkg is not None and len(gkg) > 0:
    print(f"✅ Retrieved {len(gkg):,} GKG records")
    print(f"   Dimensions: {gkg.shape[0]:,} rows × {gkg.shape[1]} columns")
    
    # Source analysis
    if 'SourceCommonName' in gkg.columns:
        print(f"\n📡 Top 10 News Sources:")
        sources = gkg['SourceCommonName'].value_counts().head(10)
        for i, (source, count) in enumerate(sources.items(), 1):
            print(f"   {i:2d}. {source:40s} → {count:4d} articles")
    
    # Location analysis
    if 'Locations' in gkg.columns:
        total_with_locations = gkg['Locations'].notna().sum()
        print(f"\n🗺️  Geographic Coverage:")
        print(f"   Records with locations: {total_with_locations:,} ({(total_with_locations/len(gkg)*100):.1f}%)")
    
    # Tone analysis
    if 'V2Tone' in gkg.columns:
        print(f"\n😊 Media Tone Analysis:")
        # V2Tone contains comma-separated values
        tone_samples = gkg['V2Tone'].dropna().head(1000)
        print(f"   Sample records with tone data: {len(tone_samples):,}")

# =============================================================================
section(5, "QUERY MENTIONS TABLE - Event Coverage")
# =============================================================================

print("\n🔍 Fetching MENTIONS from November 1, 2016...")
print("   (Shows how many times each event was mentioned across sources)")

mentions = gd2.Search('2016 Nov 1', table='mentions', output='pd')

if mentions is not None and len(mentions) > 0:
    print(f"✅ Retrieved {len(mentions):,} mentions")
    print(f"   Dimensions: {mentions.shape[0]:,} rows × {mentions.shape[1]} columns")
    
    # Event coverage analysis
    if 'GlobalEventID' in mentions.columns:
        event_counts = mentions['GlobalEventID'].value_counts()
        print(f"\n📢 Event Coverage Statistics:")
        print(f"   Unique events mentioned: {len(event_counts):,}")
        print(f"   Average mentions per event: {event_counts.mean():.1f}")
        print(f"   Max mentions for single event: {event_counts.max()}")
        
        print(f"\n🏆 Most Covered Events (by GlobalEventID):")
        for i, (event_id, count) in enumerate(event_counts.head(5).items(), 1):
            print(f"   {i}. Event #{event_id} → {count} mentions")

# =============================================================================
section(6, "DATE RANGE QUERIES")
# =============================================================================

print("\n🔍 Querying multiple days: Oct 31 - Nov 2, 2016...")
print("   (This demonstrates parallel downloading of multiple dates)")

try:
    date_range = gd2.Search(['2016 Oct 31', '2016 Nov 2'], table='events', output='pd')
    
    if date_range is not None and len(date_range) > 0:
        print(f"✅ Retrieved {len(date_range):,} events across date range")
        
        if 'SQLDATE' in date_range.columns:
            daily_counts = date_range['SQLDATE'].value_counts().sort_index()
            print(f"\n📊 Daily Event Breakdown:")
            for date, count in daily_counts.items():
                print(f"   {date}: {count:,} events")
except Exception as e:
    print(f"⚠️  Date range query: {str(e)[:80]}")

# =============================================================================
section(7, "OUTPUT FORMAT OPTIONS")
# =============================================================================

print("\n📤 gdeltPyR supports multiple output formats:")
print("   • pandas DataFrame (default)")
print("   • JSON")
print("   • CSV")
print("   • GeoPandas (for geospatial analysis)")

# JSON example
print("\n🔧 Fetching data in JSON format...")
json_data = gd2.Search('2016 Nov 1', table='events', output='json')
if json_data:
    print(f"✅ JSON output: {len(json_data):,} records")
    print(f"   Sample keys: {list(json_data[0].keys())[:5]}")

# =============================================================================
section(8, "DATA STATISTICS & ANALYSIS")
# =============================================================================

if events is not None and len(events) > 0:
    print("\n📊 COMPREHENSIVE EVENT STATISTICS:")
    
    # Numeric columns analysis
    numeric_cols = events.select_dtypes(include=['int64', 'float64']).columns
    print(f"\n🔢 Numeric Fields Available: {len(numeric_cols)}")
    
    if 'NumMentions' in events.columns:
        print(f"\n📰 Media Mentions:")
        print(f"   Total mentions: {events['NumMentions'].sum():,}")
        print(f"   Average per event: {events['NumMentions'].mean():.1f}")
        print(f"   Max mentions: {events['NumMentions'].max()}")
    
    if 'NumSources' in events.columns:
        print(f"\n📡 Source Diversity:")
        print(f"   Average sources per event: {events['NumSources'].mean():.1f}")
        print(f"   Max sources: {events['NumSources'].max()}")
    
    if 'NumArticles' in events.columns:
        print(f"\n📄 Article Coverage:")
        print(f"   Total articles: {events['NumArticles'].sum():,}")
        print(f"   Average per event: {events['NumArticles'].mean():.1f}")

# =============================================================================
section(9, "GEOGRAPHIC ANALYSIS")
# =============================================================================

if events is not None and len(events) > 0:
    print("\n🗺️  GEOGRAPHIC EVENT DISTRIBUTION:")
    
    # Action Geo locations
    geo_cols = ['ActionGeo_CountryCode', 'ActionGeo_Lat', 'ActionGeo_Long']
    geo_cols_present = [col for col in geo_cols if col in events.columns]
    
    if 'ActionGeo_CountryCode' in events.columns:
        geo_events = events[events['ActionGeo_CountryCode'].notna()]
        print(f"\n   Events with geographic data: {len(geo_events):,} ({(len(geo_events)/len(events)*100):.1f}%)")
        
        print(f"\n📍 Top 10 Event Locations (by country):")
        geo_countries = events['ActionGeo_CountryCode'].value_counts().head(10)
        for i, (country, count) in enumerate(geo_countries.items(), 1):
            print(f"   {i:2d}. {country:5s} → {count:4d} events")
    
    if 'ActionGeo_Lat' in events.columns and 'ActionGeo_Long' in events.columns:
        geo_coords = events[events['ActionGeo_Lat'].notna() & events['ActionGeo_Long'].notna()]
        print(f"\n   Events with coordinates: {len(geo_coords):,}")
        if len(geo_coords) > 0:
            print(f"   Latitude range: {geo_coords['ActionGeo_Lat'].min():.2f} to {geo_coords['ActionGeo_Lat'].max():.2f}")
            print(f"   Longitude range: {geo_coords['ActionGeo_Long'].min():.2f} to {geo_coords['ActionGeo_Long'].max():.2f}")

# =============================================================================
section(10, "CAMEO EVENT CODES")
# =============================================================================

print("\n🎯 CAMEO CODING SYSTEM:")
print("   CAMEO = Conflict and Mediation Event Observations")
print("   A standardized coding scheme for events")

if events is not None and 'EventCode' in events.columns:
    print(f"\n📋 Top 15 Event Types (by CAMEO code):")
    event_codes = events['EventCode'].value_counts().head(15)
    
    # Sample CAMEO code meanings
    cameo_meanings = {
        '010': 'Make statement',
        '042': 'Make visit',
        '043': 'Host visit',
        '051': 'Praise/endorse',
        '036': 'Express intent to cooperate',
        '040': 'Consult',
        '093': 'Split into factions',
        '112': 'Accuse',
        '120': 'Reject',
        '190': 'Use conventional military force',
    }
    
    for i, (code, count) in enumerate(event_codes.items(), 1):
        code_str = str(code) if code else 'Unknown'
        meaning = cameo_meanings.get(code_str, 'Event type')
        print(f"   {i:2d}. Code {code_str:4s} → {count:4d} events  ({meaning})")

# =============================================================================
section(11, "REAL-TIME CAPABILITIES")
# =============================================================================

print("\n⏱️  REAL-TIME MONITORING FEATURES:")
print("   • GDELT 2.0 updates every 15 minutes")
print("   • Can query specific 15-minute intervals")
print("   • Coverage reports show data availability")
print("   • Parallel downloading for faster multi-date queries")
print("   • Distinguishes between English and translated sources")

print("\n🌐 TRANSLATION TRACKING:")
print("   • Records marked with 'T' prefix are translated")
print("   • Original language identification available")
print("   • Access to global non-English media coverage")

# =============================================================================
section(12, "DATA SUMMARY")
# =============================================================================

print("\n📈 SESSION STATISTICS:")
total_records = 0
if events is not None:
    total_records += len(events)
    print(f"   ✅ Events retrieved: {len(events):,}")
if gkg is not None:
    total_records += len(gkg)
    print(f"   ✅ GKG records retrieved: {len(gkg):,}")
if mentions is not None:
    total_records += len(mentions)
    print(f"   ✅ Mentions retrieved: {len(mentions):,}")

print(f"\n   📊 TOTAL RECORDS ANALYZED: {total_records:,}")

# =============================================================================
section(13, "PRACTICAL USE CASES")
# =============================================================================

print("""
🎯 REAL-WORLD APPLICATIONS:

1. 🔴 CONFLICT MONITORING
   • Track escalation patterns in conflict zones
   • Early warning systems for humanitarian crises
   • Military/defense intelligence analysis

2. 📰 MEDIA ANALYSIS
   • Bias detection across news sources
   • Coverage comparison (US vs international media)
   • Narrative tracking over time

3. 🏛️ POLITICAL SCIENCE
   • International relations research
   • Diplomatic event analysis
   • Policy impact assessment

4. 💼 BUSINESS INTELLIGENCE
   • Country risk assessment
   • Market sentiment analysis
   • Supply chain risk monitoring

5. 🆘 CRISIS RESPONSE
   • Natural disaster tracking
   • Humanitarian needs assessment
   • Resource allocation planning

6. 📊 DATA JOURNALISM
   • Investigative reporting
   • Data-driven storytelling
   • Visual narrative creation

7. 🤖 MACHINE LEARNING
   • Event prediction models
   • Sentiment analysis training
   • Time series forecasting
""")

# =============================================================================
section(14, "ADDITIONAL FEATURES")
# =============================================================================

print("""
🔧 ADVANCED FEATURES:

✅ QUERY OPTIONS:
   • Single dates: '2016 Nov 1'
   • Date ranges: ['2016 Oct 31', '2016 Nov 2']
   • Multiple specific dates: ['2016 Nov 1', '2016 Nov 5', '2016 Nov 10']

✅ TABLE OPTIONS:
   • events: Core event data
   • gkg: Global Knowledge Graph
   • mentions: Event mention tracking

✅ OUTPUT FORMATS:
   • pd: Pandas DataFrame
   • json: JSON objects
   • csv: CSV string
   • gpd: GeoPandas DataFrame (for mapping)

✅ FILTERING:
   • normcols: Normalize column names
   • coverage: Show data availability
   • translation: Filter English vs translated

✅ PERFORMANCE:
   • Parallel HTTP requests
   • Automatic retry logic
   • Efficient data compression
   • Memory-optimized processing
""")

# =============================================================================
banner("DEMONSTRATION COMPLETE!")
# =============================================================================

print("\n✨ You've now seen EVERYTHING gdeltPyR can do!")
print("\n📚 NEXT STEPS:")
print("   1. Explore the examples/ directory for Jupyter notebooks")
print("   2. Check out the CAMEO codebook for event codes")
print("   3. Read the documentation at https://linwoodc3.github.io/gdeltPyR/")
print("   4. Start building your own analysis!")

print("\n💡 QUICK START CODE:")
print("""
   import gdelt
   gd = gdelt.gdelt(version=2)
   
   # Get today's events
   events = gd.Search('2016 Nov 1', table='events')
   
   # Analyze specific country
   usa_events = events[events['Actor1CountryCode'] == 'USA']
   
   # Export to CSV
   events.to_csv('my_events.csv', index=False)
""")

print("\n" + "="*80)
print("🌍 GDELT: The World in Real-Time Data 🌍")
print("="*80 + "\n")
