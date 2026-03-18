"""
🌍 COMPLETE gdeltPyR SHOWCASE - ALL FEATURES! 🌍
"""
import gdelt
import pandas as pd

print("="*80)
print("         🌍 GDELT PyR - ULTIMATE DEMONSTRATION 🌍")
print("="*80)
print()

# ============================================================================
print("✅ STEP 1: Initialize GDELT")
print("-" * 80)
print("   GDELT v1.0: Daily updates, historical data from 1979")
print("   GDELT v2.0: 15-minute updates, from February 2015")
print()

gd1 = gdelt.gdelt(version=1)
gd2 = gdelt.gdelt(version=2)
print("   ✓ Both versions initialized successfully!")

# ============================================================================
print("\n✅ STEP 2: Explore Available Tables & Schemas")
print("-" * 80)

events_schema = gd2.schema('events')
gkg_schema = gd2.schema('gkg')

print(f"   EVENTS table: {len(events_schema)} columns")
print(f"   GKG table: {len(gkg_schema)} columns")
print(f"   MENTIONS table: Available for tracking event coverage")

# ============================================================================
print("\n✅ STEP 3: Query EVENTS Data")
print("-" * 80)
print("   Fetching events from November 1, 2016...")

events = gd2.Search('2016 Nov 1', table='events', output='pd')

print(f"\n   📊 RETRIEVED: {len(events):,} events")
print(f"   📁 DIMENSIONS: {events.shape[0]:,} rows × {events.shape[1]} columns")

# ============================================================================
print("\n✅ STEP 4: Analyze Event Data")
print("-" * 80)

# Top Actors
print("\n   👥 TOP 10 ACTORS:")
top_actors = events['Actor1Name'].value_counts().head(10)
for i, (actor, count) in enumerate(top_actors.items(), 1):
    print(f"      {i:2}. {actor:30s} {count:4} events")

# Top Countries
print("\n   🌍 TOP 10 COUNTRIES:")
countries = events['Actor1CountryCode'].value_counts().head(10)
for i, (country, count) in enumerate(countries.items(), 1):
    print(f"      {i:2}. {country:5s} {count:4} events")

# Event Categories
print("\n   🎭 EVENT CATEGORIES:")
quad_names = {1: "Verbal Cooperation", 2: "Material Cooperation", 
              3: "Verbal Conflict", 4: "Material Conflict"}
for quad in sorted(events['QuadClass'].unique()):
    count = (events['QuadClass'] == quad).sum()
    pct = (count / len(events)) * 100
    print(f"      {quad_names[quad]:25s} {count:4} ({pct:5.1f}%)")

# Goldstein Scale
avg_tone = events['GoldsteinScale'].mean()
print(f"\n   📈 TONE ANALYSIS:")
print(f"      Average Goldstein Score: {avg_tone:.2f}")
print(f"      (Negative = conflict, Positive = cooperation)")

# ============================================================================
print("\n✅ STEP 5: Query GLOBAL KNOWLEDGE GRAPH (GKG)")
print("-" * 80)
print("   Fetching GKG data...")

gkg = gd2.Search('2016 Nov 1', table='gkg', output='pd')

print(f"\n   📊 RETRIEVED: {len(gkg):,} GKG records")

# Top Sources
print("\n   📡 TOP 10 NEWS SOURCES:")
sources = gkg['SourceCommonName'].value_counts().head(10)
for i, (source, count) in enumerate(sources.items(), 1):
    print(f"      {i:2}. {source:40s} {count:3} articles")

# Geographic coverage
geo_count = gkg['Locations'].notna().sum()
geo_pct = (geo_count / len(gkg)) * 100
print(f"\n   🗺️  GEOGRAPHIC DATA: {geo_count:,} records ({geo_pct:.1f}%) have location info")

# ============================================================================
print("\n✅ STEP 6: Query MENTIONS Data")
print("-" * 80)
print("   Fetching mentions data...")

mentions = gd2.Search('2016 Nov 1', table='mentions', output='pd')

print(f"\n   📊 RETRIEVED: {len(mentions):,} mentions")

# Event coverage
unique_events = mentions['GlobalEventID'].nunique()
avg_mentions = mentions['GlobalEventID'].value_counts().mean()
max_mentions = mentions['GlobalEventID'].value_counts().max()

print(f"\n   📢 COVERAGE ANALYSIS:")
print(f"      Unique events mentioned: {unique_events:,}")
print(f"      Average mentions per event: {avg_mentions:.1f}")
print(f"      Max mentions for one event: {int(max_mentions)}")

# ============================================================================
print("\n✅ STEP 7: Geographic Analysis")
print("-" * 80)

geo_events = events[events['ActionGeo_CountryCode'].notna()]
print(f"\n   Events with geographic data: {len(geo_events):,} ({(len(geo_events)/len(events)*100):.1f}%)")

print("\n   📍 TOP EVENT LOCATIONS:")
locations = events['ActionGeo_CountryCode'].value_counts().head(10)
for i, (country, count) in enumerate(locations.items(), 1):
    print(f"      {i:2}. {country:5s} {count:4} events")

# Coordinates
has_coords = events['ActionGeo_Lat'].notna() & events['ActionGeo_Long'].notna()
print(f"\n   Events with GPS coordinates: {has_coords.sum():,}")

# ============================================================================
print("\n✅ STEP 8: CAMEO Event Code Analysis")
print("-" * 80)

cameo_meanings = {
    '010': 'Make statement', '042': 'Make visit', '043': 'Host visit',
    '051': 'Praise/endorse', '036': 'Express intent to cooperate',
    '040': 'Consult', '112': 'Accuse', '120': 'Reject'
}

print("\n   🎯 TOP CAMEO EVENT CODES:")
event_codes = events['EventCode'].value_counts().head(10)
for i, (code, count) in enumerate(event_codes.items(), 1):
    code_str = str(int(code)) if pd.notna(code) else 'Unknown'
    meaning = cameo_meanings.get(code_str, 'Event type')
    print(f"      {i:2}. Code {code_str:4s} → {count:4} ({meaning})")

# ============================================================================
print("\n✅ STEP 9: Data Statistics")
print("-" * 80)

if 'NumMentions' in events.columns:
    print(f"\n   📰 MEDIA MENTIONS:")
    print(f"      Total mentions: {events['NumMentions'].sum():,}")
    print(f"      Average per event: {events['NumMentions'].mean():.1f}")
    print(f"      Max mentions: {int(events['NumMentions'].max())}")

if 'NumSources' in events.columns:
    print(f"\n   📡 SOURCE DIVERSITY:")
    print(f"      Average sources per event: {events['NumSources'].mean():.1f}")

if 'NumArticles' in events.columns:
    print(f"\n   📄 ARTICLE COVERAGE:")
    print(f"      Total articles: {events['NumArticles'].sum():,}")
    print(f"      Average per event: {events['NumArticles'].mean():.1f}")

# ============================================================================
print("\n✅ STEP 10: Sample Event Details")
print("-" * 80)

sample = events.head(5)
print("\n   📰 First 5 Events:")
print()
for idx, row in sample.iterrows():
    print(f"   Event #{int(row['GLOBALEVENTID'])}:")
    print(f"      Date: {row['SQLDATE']}")
    print(f"      Actor1: {row['Actor1Name']}")
    print(f"      Actor2: {row['Actor2Name']}")
    print(f"      Event Type: Code {int(row['EventCode']) if pd.notna(row['EventCode']) else 'N/A'}")
    print(f"      Goldstein Score: {row['GoldsteinScale']:.1f}")
    print()

# ============================================================================
print("="*80)
print("                    📊 SESSION SUMMARY")
print("="*80)

total_records = len(events) + len(gkg) + len(mentions)

print(f"""
   ✅ Events retrieved: {len(events):,}
   ✅ GKG records retrieved: {len(gkg):,}
   ✅ Mentions retrieved: {len(mentions):,}
   
   📊 TOTAL RECORDS: {total_records:,}
""")

# ============================================================================
print("="*80)
print("                    🚀 CAPABILITIES DEMONSTRATED")
print("="*80)

print("""
✓ Multiple table types (events, gkg, mentions)
✓ Real-time data retrieval from GDELT servers
✓ Comprehensive data analysis and statistics
✓ Geographic event tracking
✓ CAMEO event coding system
✓ Media source analysis
✓ Event coverage tracking
✓ Actor and country identification
✓ Sentiment/tone analysis (Goldstein Scale)
✓ Pandas DataFrame integration
""")

# ============================================================================
print("="*80)
print("                    💡 REAL-WORLD APPLICATIONS")
print("="*80)

print("""
🔴 CONFLICT MONITORING
   • Track escalation in conflict zones
   • Early warning systems
   • Defense intelligence

📰 MEDIA ANALYSIS
   • Bias detection
   • Coverage comparison
   • Narrative tracking

🏛️ POLITICAL SCIENCE
   • International relations research
   • Diplomatic event analysis
   • Policy impact studies

💼 BUSINESS INTELLIGENCE
   • Country risk assessment
   • Market sentiment
   • Supply chain monitoring

🆘 CRISIS RESPONSE
   • Disaster tracking
   • Humanitarian assessment
   • Resource planning

📊 DATA JOURNALISM
   • Investigative reporting
   • Data storytelling
   • Visual narratives
""")

# ============================================================================
print("="*80)
print("                    📚 QUICK START CODE")
print("="*80)

print("""
import gdelt

# Initialize
gd = gdelt.gdelt(version=2)

# Get events
events = gd.Search('2016 Nov 1', table='events')

# Filter by country
usa = events[events['Actor1CountryCode'] == 'USA']

# Export
events.to_csv('my_events.csv', index=False)

# Date range query
multi = gd.Search(['2016 Oct 31', '2016 Nov 2'], table='events')
""")

# ============================================================================
print("="*80)
print("          ✨ DEMONSTRATION COMPLETE! ✨")
print("="*80)
print()
print("🌍 GDELT: Monitoring the World in Real-Time 🌍")
print()
print("Documentation: https://linwoodc3.github.io/gdeltPyR/")
print("="*80)
