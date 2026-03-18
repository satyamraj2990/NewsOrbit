"""
NewsOrbit
Global Intelligence Platform for real-time events monitoring
"""
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import gdelt
import pandas as pd
from datetime import datetime, timedelta
import json
import sys
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'newsOrbit_intel_2024_xKp9'
CORS(app)

# --- Auth helpers ---
DASHBOARD_USER = 'admin'
DASHBOARD_PASS = 'newsOrbit2024'

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# Initialize GDELT - lazy loading to avoid issues
gd1 = None
gd2 = None

def get_gdelt(version=2):
    """Lazy load GDELT instances"""
    global gd1, gd2
    if version == 1:
        if gd1 is None:
            gd1 = gdelt.gdelt(version=1)
        return gd1
    else:
        if gd2 is None:
            gd2 = gdelt.gdelt(version=2)
        return gd2

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if session.get('logged_in'):
        return redirect(url_for('index'))
    error = None
    username = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if username == DASHBOARD_USER and password == DASHBOARD_PASS:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password. Please try again.'
    return render_template('login.html', error=error, username=username)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Main dashboard page"""
    from flask import make_response
    resp = make_response(render_template('index.html'))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    return resp

@app.route('/api/query', methods=['POST'])
def query_gdelt():
    """Query GDELT data based on user input"""
    from datetime import datetime, timedelta
    
    try:
        data = request.json
        date = data.get('date', '2016 Nov 1')
        table = data.get('table', 'events')
        version = data.get('version', 2)
        
        print(f"Query received: date={date}, table={table}, version={version}", file=sys.stderr)
        
        # Select version
        gd = get_gdelt(version)
        
        # Query data
        print(f"Querying GDELT...", file=sys.stderr)
        results = gd.Search(date, table=table, output='pd')
        
        if results is None or len(results) == 0:
            print(f"No data found for {date}", file=sys.stderr)
            
            # Provide helpful suggestions
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            last_week = today - timedelta(days=7)
            
            suggestions = [
                f"{yesterday.year} {yesterday.strftime('%b')} {yesterday.day}",
                f"{last_week.year} {last_week.strftime('%b')} {last_week.day}",
                "2024 Jan 1",
                "2023 Dec 15"
            ]
            
            error_response = {
                'error': 'No data available for this date/table combination',
                'message': 'GDELT may not have published data for this date yet. Try a date from a few days ago.',
                'query_date': date,
                'suggestions': suggestions,
                'note': f'GDELT {version}.0 data may have a delay of several hours to days for recent dates.'
            }
            return jsonify(error_response), 404
        
        print(f"Got {len(results)} records", file=sys.stderr)
        
        # Replace NaN values with None for valid JSON
        results_clean = results.head(10).fillna('')
        
        # Add metadata about the query
        
        # Prepare response
        response = {
            'total_records': len(results),
            'columns': results.columns.tolist(),
            'sample_data': results_clean.to_dict('records'),
            'trending_news': get_trending_news(results, table),
            'stats': get_statistics(results, table),
            'metadata': {
                'query_date': date,
                'table': table,
                'version': f'GDELT {version}.0',
                'fetched_at': datetime.now().isoformat(),
                'source': f'GDELT {"2.0 (15-minute updates)" if version == 2 else "1.0 (daily updates)"}',
                'live_data': True
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        
        # Provide helpful suggestions
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)
        
        suggestions = [
            f"{yesterday.year} {yesterday.strftime('%b')} {yesterday.day}",
            f"{last_week.year} {last_week.strftime('%b')} {last_week.day}",
            "2024 Jan 1",
            "2023 Dec 15"
        ]
        
        error_response = {
            'error': 'Failed to retrieve data',
            'message': str(e) if 'no data' in str(e).lower() else 'An error occurred while querying GDELT. The date may be too recent or the table may not have data.',
            'query_date': data.get('date', 'Unknown'),
            'suggestions': suggestions,
            'note': f'GDELT {version}.0 data may have a delay of several hours to days for recent dates. Try a date from a few days ago.'
        }
        return jsonify(error_response), 404

@app.route('/api/schema/<table>')
def get_schema(table):
    """Get schema information for a table"""
    try:
        gd = get_gdelt(2)
        schema = gd.schema(table)
        return jsonify({
            'table': table,
            'columns': len(schema),
            'schema': schema.to_dict('records')
        })
    except Exception as e:
        print(f"Error in schema: {str(e)}", file=sys.stderr)
    """Get schema information for a table"""
    try:
        schema = gd2.schema(table)
        return jsonify({
            'table': table,
            'columns': len(schema),
            'schema': schema.to_dict('records')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def classify_event_domain(row):
    """Classify event into domain based on event code, actors, and description"""
    # Get event code as string
    event_code = str(row.get('EventCode', ''))
    actor1 = str(row.get('Actor1Name', '')).lower()
    actor2 = str(row.get('Actor2Name', '')).lower()
    
    # Event code mappings (CAMEO codes)
    # Politics: 01-04 (statements, appeals, express intent, demand)
    if event_code.startswith(('01', '02', '03', '04')):
        if any(word in actor1 or word in actor2 for word in ['bank', 'fed', 'finance', 'trade', 'economy']):
            return 'Finance'
        return 'Politics'
    
    # Diplomacy: 05-07 (engage in diplomatic cooperation, consult, provide aid)
    elif event_code.startswith(('05', '06', '07')):
        if any(word in actor1 or word in actor2 for word in ['health', 'medical', 'hospital', 'disease']):
            return 'Health'
        return 'Diplomacy'
    
    # Material cooperation: 08 (yield, economic/military cooperation)
    elif event_code.startswith('08'):
        if any(word in actor1 or word in actor2 for word in ['hospital', 'health', 'medical']):
            return 'Health'
        return 'Economy'
    
    # Investigations: 09-10 (investigate, demand)
    elif event_code.startswith(('09', '10')):
        return 'Politics'
    
    # Disapprove/Reject: 11-12
    elif event_code.startswith(('11', '12')):
        return 'Politics'
    
    # Threaten: 13
    elif event_code.startswith('13'):
        return 'Security'
    
    # Protest: 14
    elif event_code.startswith('14'):
        return 'Society'
    
    # Exhibit force posture: 15
    elif event_code.startswith('15'):
        return 'Security'
    
    # Reduce relations: 16
    elif event_code.startswith('16'):
        return 'Diplomacy'
    
    # Coerce: 17
    elif event_code.startswith('17'):
        return 'Security'
    
    # Assault: 18
    elif event_code.startswith('18'):
        return 'Security'
    
    # Fight: 19
    elif event_code.startswith('19'):
        return 'Security'
    
    # Unconventional violence: 20
    elif event_code.startswith('20'):
        return 'Security'
    
    # Check actors for additional context
    if any(word in actor1 or word in actor2 for word in ['school', 'student', 'university', 'education', 'teacher']):
        return 'Education'
    elif any(word in actor1 or word in actor2 for word in ['company', 'business', 'startup', 'tech', 'cyber']):
        return 'Business'
    elif any(word in actor1 or word in actor2 for word in ['climate', 'environment', 'pollution', 'flood', 'earthquake']):
        return 'Environment'
    elif any(word in actor1 or word in actor2 for word in ['science', 'research', 'laboratory']):
        return 'Science'
    
    # Default
    return 'General'

def get_trending_news(df, table):
    """Extract top 7 trending news items sorted by mention count / tone prominence."""
    from urllib.parse import urlparse
    news = []
    try:
        if table == 'events':
            if 'SOURCEURL' not in df.columns:
                return []
            df_f = df[df['SOURCEURL'].notna() & df['SOURCEURL'].astype(str).str.startswith('http')].copy()
            if 'NumMentions' in df_f.columns:
                df_f['NumMentions'] = pd.to_numeric(df_f['NumMentions'], errors='coerce').fillna(0)
                df_f = df_f.sort_values('NumMentions', ascending=False)
            quad_icons = {1: '🤝', 2: '🤝', 3: '⚡', 4: '💥'}
            seen = set()
            for _, row in df_f.iterrows():
                url = str(row.get('SOURCEURL', ''))
                if url in seen or not url.startswith('http'):
                    continue
                seen.add(url)
                a1 = str(row.get('Actor1Name', '')).strip()
                a2 = str(row.get('Actor2Name', '')).strip()
                actors = [a for a in [a1, a2] if a and a.lower() not in ('unknown', 'nan', '')]
                if len(actors) >= 2:
                    title = f"{actors[0]} — {actors[1]}"
                elif len(actors) == 1:
                    title = actors[0]
                else:
                    title = f"Global Event ({row.get('EventCode', '')})"
                quad = int(row.get('QuadClass', 0)) if pd.notna(row.get('QuadClass', 0)) else 0
                try:
                    source = urlparse(url).netloc.replace('www.', '')
                except Exception:
                    source = 'source'
                news.append({
                    'title': title[:120],
                    'url': url,
                    'source': source,
                    'country': str(row.get('Actor1CountryCode', '')).strip(),
                    'mentions': int(row.get('NumMentions', 0)) if pd.notna(row.get('NumMentions', 0)) else 0,
                    'goldstein': round(float(row.get('GoldsteinScale', 0.0)), 1) if pd.notna(row.get('GoldsteinScale', 0.0)) else 0.0,
                    'domain': classify_event_domain(row.to_dict()),
                    'quad_icon': quad_icons.get(quad, '📰'),
                    'date': str(row.get('SQLDATE', ''))
                })
                if len(news) >= 7:
                    break

        elif table == 'gkg':
            url_col = next((c for c in ['DocumentIdentifier', 'GKGRECORDID'] if c in df.columns), None)
            if not url_col:
                return []
            df_f = df[df[url_col].notna() & df[url_col].astype(str).str.startswith('http')].copy()
            seen = set()
            for _, row in df_f.iterrows():
                url = str(row.get(url_col, ''))
                if url in seen or not url.startswith('http'):
                    continue
                seen.add(url)
                source = str(row.get('SourceCommonName', '') or row.get('V2SourceCommonName', ''))
                if not source or source == 'nan':
                    try:
                        source = urlparse(url).netloc.replace('www.', '')
                    except Exception:
                        source = 'source'
                themes_raw = str(row.get('V2Themes', '') or row.get('Themes', ''))
                top_theme = themes_raw.split(';')[0].split(',')[0][:60] if themes_raw and themes_raw != 'nan' else source
                tone_raw = str(row.get('V2Tone', '0'))
                try:
                    tone_val = round(float(tone_raw.split(',')[0]), 1)
                except Exception:
                    tone_val = 0.0
                news.append({
                    'title': top_theme,
                    'url': url,
                    'source': source[:50],
                    'country': '',
                    'mentions': 0,
                    'goldstein': tone_val,
                    'domain': 'News',
                    'quad_icon': '📰',
                    'date': str(row.get('DATE', ''))
                })
                if len(news) >= 7:
                    break

        elif table == 'mentions':
            url_col = 'MentionIdentifier' if 'MentionIdentifier' in df.columns else None
            if not url_col:
                return []
            df_f = df[df[url_col].notna() & df[url_col].astype(str).str.startswith('http')].copy()
            if 'MentionDocTone' in df_f.columns:
                df_f['_abs_tone'] = df_f['MentionDocTone'].apply(lambda x: abs(float(x)) if pd.notna(x) else 0)
                df_f = df_f.sort_values('_abs_tone', ascending=False)
            seen = set()
            for _, row in df_f.iterrows():
                url = str(row.get(url_col, ''))
                if url in seen or not url.startswith('http'):
                    continue
                seen.add(url)
                try:
                    source = urlparse(url).netloc.replace('www.', '')
                except Exception:
                    source = 'source'
                tone = round(float(row.get('MentionDocTone', 0.0)), 1) if pd.notna(row.get('MentionDocTone', 0.0)) else 0.0
                news.append({
                    'title': f"Coverage by {source}",
                    'url': url,
                    'source': source,
                    'country': '',
                    'mentions': 0,
                    'goldstein': tone,
                    'domain': 'Mentions',
                    'quad_icon': '🔔',
                    'date': str(row.get('MentionTimeDate', ''))
                })
                if len(news) >= 7:
                    break
    except Exception as e:
        import sys
        print(f"Trending news error: {e}", file=sys.stderr)
    return news

def get_statistics(df, table):
    """Generate statistics based on table type"""
    stats = {
        'total_records': len(df),
        'shape': df.shape
    }
    
    if table == 'events':
        # Build hierarchical structure: Country → Domain → Events
        hierarchical_data = {}
        
        if 'Actor1CountryCode' in df.columns:
            # Group by country — skip rows with no country code
            for country_code in df['Actor1CountryCode'].unique():
                if pd.isna(country_code) or str(country_code).strip() == '':
                    continue  # skip unknown/missing countries
                country_code = str(country_code).strip()
                
                country_df = df[df['Actor1CountryCode'] == country_code]
                
                # Classify events into domains
                country_df['Domain'] = country_df.apply(classify_event_domain, axis=1)
                
                # Get domain distribution
                domains = {}
                for domain in country_df['Domain'].unique():
                    domain_df = country_df[country_df['Domain'] == domain]
                    
                    # Get average tone for domain
                    avg_tone = float(domain_df['GoldsteinScale'].mean()) if 'GoldsteinScale' in domain_df.columns else 0.0
                    
                    # Get events for this domain (limit to 20 per domain)
                    events = []
                    for idx, event in domain_df.head(20).iterrows():
                        events.append({
                            'date': str(event.get('SQLDATE', '')),
                            'actor1': str(event.get('Actor1Name', 'Unknown'))[:50],
                            'actor2': str(event.get('Actor2Name', 'Unknown'))[:50],
                            'event_code': str(event.get('EventCode', '')),
                            'goldstein': float(event.get('GoldsteinScale', 0.0)) if pd.notna(event.get('GoldsteinScale')) else 0.0,
                            'quad_class': int(event.get('QuadClass', 0)) if pd.notna(event.get('QuadClass')) else 0,
                            'source_url': str(event.get('SOURCEURL', ''))[:200] if 'SOURCEURL' in event and pd.notna(event.get('SOURCEURL')) else '',
                            'num_mentions': int(event.get('NumMentions', 0)) if 'NumMentions' in event and pd.notna(event.get('NumMentions')) else 0,
                            'num_sources': int(event.get('NumSources', 0)) if 'NumSources' in event and pd.notna(event.get('NumSources')) else 0,
                            'avg_tone': float(event.get('AvgTone', 0.0)) if 'AvgTone' in event and pd.notna(event.get('AvgTone')) else 0.0
                        })
                    
                    domains[domain] = {
                        'count': int(len(domain_df)),
                        'avg_tone': round(avg_tone, 2),
                        'events': events
                    }
                
                # Get dominant domain
                dominant_domain = max(domains.items(), key=lambda x: x[1]['count'])[0] if domains else 'Unknown'
                
                hierarchical_data[country_code] = {
                    'total_events': int(len(country_df)),
                    'dominant_domain': dominant_domain,
                    'domains': domains
                }
        
        # Sort countries by event count
        sorted_countries = dict(sorted(hierarchical_data.items(), key=lambda x: x[1]['total_events'], reverse=True))
        stats['hierarchical_data'] = sorted_countries
        
        # Keep legacy stats for backward compatibility
        if 'Actor1CountryCode' in df.columns:
            top_countries = df['Actor1CountryCode'].value_counts().head(10).to_dict()
            stats['top_countries'] = {str(k) if pd.notna(k) else 'Unknown': int(v) for k, v in top_countries.items()}
        
        if 'Actor1Name' in df.columns:
            top_actors = df['Actor1Name'].value_counts().head(10).to_dict()
            stats['top_actors'] = {str(k) if pd.notna(k) else 'Unknown': int(v) for k, v in top_actors.items()}
        
        if 'QuadClass' in df.columns:
            quad_map = {
                1: "Verbal Cooperation",
                2: "Material Cooperation",
                3: "Verbal Conflict",
                4: "Material Conflict"
            }
            quad_counts = df['QuadClass'].value_counts().to_dict()
            stats['event_categories'] = {
                quad_map.get(k, f"Category {k}"): v 
                for k, v in quad_counts.items()
            }
        
        if 'GoldsteinScale' in df.columns:
            stats['goldstein_avg'] = float(df['GoldsteinScale'].mean())
            stats['goldstein_min'] = float(df['GoldsteinScale'].min())
            stats['goldstein_max'] = float(df['GoldsteinScale'].max())
        
        if 'EventCode' in df.columns:
            top_codes = df['EventCode'].value_counts().head(10).to_dict()
            stats['top_event_codes'] = {str(k) if pd.notna(k) else 'Unknown': int(v) for k, v in top_codes.items()}
    
    elif table == 'gkg':
        # Top sources
        if 'SourceCommonName' in df.columns:
            top_sources = df['SourceCommonName'].value_counts().head(10).to_dict()
            stats['top_sources'] = {str(k) if pd.notna(k) else 'Unknown': int(v) for k, v in top_sources.items()}

        # Location coverage
        if 'Locations' in df.columns:
            stats['with_locations'] = int(df['Locations'].notna().sum())
            stats['location_percentage'] = float((df['Locations'].notna().sum() / len(df)) * 100)

        # Top themes (semicolon-separated)
        if 'Themes' in df.columns:
            try:
                themes_series = df['Themes'].dropna().str.split(';').explode()
                top_themes = themes_series[themes_series.str.strip() != ''].value_counts().head(15).to_dict()
                stats['top_themes'] = {str(k): int(v) for k, v in top_themes.items()}
            except Exception:
                stats['top_themes'] = {}

        # Top persons from V2Persons (name,offset;name,offset)
        if 'V2Persons' in df.columns:
            try:
                def _extract_names(s):
                    if pd.isna(s): return []
                    return [p.split(',')[0].strip() for p in str(s).split(';') if ',' in p]
                persons = df['V2Persons'].apply(_extract_names).explode()
                top_persons = persons[persons.notna() & (persons != '')].value_counts().head(10).to_dict()
                stats['top_persons'] = {str(k): int(v) for k, v in top_persons.items()}
            except Exception:
                stats['top_persons'] = {}

        # Top organizations
        if 'V2Organizations' in df.columns:
            try:
                def _extract_orgs(s):
                    if pd.isna(s): return []
                    return [o.split(',')[0].strip() for o in str(s).split(';') if ',' in o]
                orgs = df['V2Organizations'].apply(_extract_orgs).explode()
                top_orgs = orgs[orgs.notna() & (orgs != '')].value_counts().head(10).to_dict()
                stats['top_organizations'] = {str(k): int(v) for k, v in top_orgs.items()}
            except Exception:
                stats['top_organizations'] = {}

        # Average tone (V2Tone: comma-separated, first value = overall tone)
        if 'V2Tone' in df.columns:
            try:
                tones = df['V2Tone'].dropna().apply(lambda s: float(str(s).split(',')[0]))
                if len(tones):
                    stats['avg_tone'] = round(float(tones.mean()), 2)
            except Exception:
                pass

        # Article cards for explorer (top 40 rows)
        articles = []
        for _, row in df.head(40).iterrows():
            themes_raw = row.get('Themes', '')
            themes = [t.strip() for t in str(themes_raw).split(';')[:5] if t.strip()] if pd.notna(themes_raw) else []
            tone = None
            v2tone = row.get('V2Tone', '')
            if pd.notna(v2tone):
                try:
                    tone = round(float(str(v2tone).split(',')[0]), 2)
                except Exception:
                    pass
            persons_raw = row.get('V2Persons', '')
            persons = []
            if pd.notna(persons_raw):
                persons = [p.split(',')[0].strip() for p in str(persons_raw).split(';')[:3] if ',' in p]
            articles.append({
                'source': str(row.get('SourceCommonName', 'Unknown'))[:60],
                'url': str(row.get('DocumentIdentifier', ''))[:150],
                'date': str(row.get('DATE', '')),
                'themes': themes,
                'tone': tone,
                'persons': persons,
            })
        stats['articles'] = articles

    elif table == 'mentions':
        print(f"Mentions columns: {df.columns.tolist()}", file=sys.stderr)
        # NOTE: actual column name is GLOBALEVENTID (all caps)
        if 'GLOBALEVENTID' in df.columns:
            unique_events = df['GLOBALEVENTID'].nunique()
            event_counts = df['GLOBALEVENTID'].value_counts()
            avg_mentions = float(event_counts.mean())
            max_mentions = int(event_counts.max())
            stats['unique_events'] = int(unique_events)
            stats['avg_mentions_per_event'] = round(avg_mentions, 2)
            stats['max_mentions'] = max_mentions
            print(f"Mentions stats: unique={unique_events}, avg={avg_mentions}, max={max_mentions}", file=sys.stderr)

            # Top mention sources
            if 'MentionSourceName' in df.columns:
                top_sources = df['MentionSourceName'].value_counts().head(10).to_dict()
                stats['top_mention_sources'] = {str(k): int(v) for k, v in top_sources.items()}

            # Mention type distribution
            if 'MentionType' in df.columns:
                mention_type_map = {1: 'WEB', 2: 'Citation Only', 3: 'Core', 4: 'DTIC', 5: 'JSTOR', 6: 'Non-Textual'}
                type_counts = df['MentionType'].value_counts().to_dict()
                stats['mention_types'] = {
                    mention_type_map.get(int(k), str(k)): int(v)
                    for k, v in type_counts.items() if pd.notna(k)
                }

            # Average confidence and doc tone
            if 'Confidence' in df.columns:
                stats['avg_confidence'] = round(float(df['Confidence'].dropna().mean()), 1)
            if 'MentionDocTone' in df.columns:
                stats['avg_doc_tone'] = round(float(df['MentionDocTone'].dropna().mean()), 2)

            # Top events by mention count (for the explorer)
            try:
                top_events_list = []
                for event_id, grp_df in sorted(
                    df.groupby('GLOBALEVENTID'), key=lambda x: -len(x[1])
                )[:30]:
                    entry = {'event_id': int(event_id), 'mention_count': int(len(grp_df))}
                    entry['sources'] = [str(s)[:60] for s in grp_df['MentionSourceName'].dropna().unique()[:5]] if 'MentionSourceName' in grp_df.columns else []
                    entry['avg_confidence'] = round(float(grp_df['Confidence'].dropna().mean()), 1) if 'Confidence' in grp_df.columns and len(grp_df['Confidence'].dropna()) else 0
                    entry['avg_tone'] = round(float(grp_df['MentionDocTone'].dropna().mean()), 2) if 'MentionDocTone' in grp_df.columns and len(grp_df['MentionDocTone'].dropna()) else 0
                    entry['first_mention'] = str(grp_df['MentionTimeDate'].min()) if 'MentionTimeDate' in grp_df.columns else ''
                    entry['last_mention'] = str(grp_df['MentionTimeDate'].max()) if 'MentionTimeDate' in grp_df.columns else ''
                    top_events_list.append(entry)
                stats['top_mentioned_events'] = top_events_list
            except Exception as ex:
                print(f"Mentions groupby error: {ex}", file=sys.stderr)
                stats['top_mentioned_events'] = []
        else:
            print(f"WARNING: GLOBALEVENTID column not found. Columns: {df.columns.tolist()}", file=sys.stderr)
            stats['unique_events'] = 0
            stats['avg_mentions_per_event'] = 0.0
            stats['max_mentions'] = 0
            stats['top_mentioned_events'] = []

    return stats

@app.route('/api/quick-query')
def quick_query():
    """Quick query for dashboard overview"""
    try:
        gd = get_gdelt(2)
        events = gd.Search('2016 Nov 1', table='events', output='pd')
        
        # Clean sample events
        sample_clean = events[['SQLDATE', 'Actor1Name', 'Actor2Name', 'EventCode']].head(5).fillna('')
        
        response = {
            'total_events': len(events),
            'top_countries': {str(k) if pd.notna(k) else 'Unknown': int(v) for k, v in events['Actor1CountryCode'].value_counts().head(5).items()},
            'event_distribution': {int(k): int(v) for k, v in events['QuadClass'].value_counts().items()},
            'avg_tone': float(events['GoldsteinScale'].mean()),
            'sample_events': sample_clean.to_dict('records')
        }
        
        return jsonify(response)
    except Exception as e:
        print(f"Error in quick-query: {str(e)}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

GEMINI_API_KEY = (os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') or '').strip()
GEMINI_MODELS = [
    'gemini-2.0-flash',
    'gemini-2.0-flash-lite',
    'gemini-1.5-flash',
    'gemini-1.5-flash-8b',
]

import hashlib, time as _time, re as _re

_ai_cache = {}
_ai_call_times = []
_ai_quota_exhausted_until = 0   # epoch time — skip Gemini until this time
_AI_CACHE_TTL = 600
_AI_MAX_RPM   = 10

def _normalize(text):
    return _re.sub(r'[^a-z0-9 ]', '', text.lower().strip())

def _cache_key(message, context_str, language):
    raw = f"{_normalize(message)}|{context_str[:200]}|{language}"
    return hashlib.md5(raw.encode()).hexdigest()

def _rpm_ok():
    now = _time.time()
    _ai_call_times[:] = [t for t in _ai_call_times if now - t < 60]
    return len(_ai_call_times) < _AI_MAX_RPM

def _gemini_available():
    """False if quota was exhausted recently (wait 1 hour before retrying)."""
    return bool(GEMINI_API_KEY) and _time.time() > _ai_quota_exhausted_until

def _local_answer(message, ctx):
    """Always returns a useful markdown string regardless of context."""
    msg        = _normalize(message)
    countries  = ctx.get('top_countries') or {}
    top_c      = sorted(countries.items(), key=lambda x: -x[1])[:8]
    gold       = ctx.get('goldstein_avg')
    total      = ctx.get('total_records') or 0
    date       = ctx.get('date') or 'today'
    domains    = ctx.get('top_domains') or {}

    no_data = (total == 0 and not top_c)

    def fmt_countries():
        if not top_c:
            return '• No country data loaded yet — run a GDELT query first'
        return '\n'.join(f'• **{c}** — {n:,} events' for c, n in top_c)

    def fmt_stability():
        if gold is None:
            return '• Stability index not available — run a GDELT query first'
        label = ('highly stable'       if gold > 3  else
                 'moderately stable'   if gold > 0  else
                 'tense / conflict-prone' if gold > -3 else
                 'highly conflictual')
        bar = '🟢' if gold > 3 else '🟡' if gold > 0 else '🟠' if gold > -3 else '🔴'
        return f'• {bar} Global Goldstein average: **{gold:.2f}** — **{label}**'

    def fmt_domains():
        if not domains:
            return ''
        lines = [f'• {d}: {n} articles' for d, n in list(domains.items())[:5]]
        return '\n'.join(lines)

    # ── No data loaded yet ──────────────────────────────────────────────
    if no_data:
        msg_lower = msg

        # Answer common general questions from static knowledge
        if any(w in msg_lower for w in ['conflict','war','attack','fight','battle','crisis','killing','violence']):
            return (
                '## 🌍 Major Ongoing Conflicts (General Knowledge)\n'
                '• **Russia–Ukraine War** — ongoing large-scale conflict since Feb 2022; frontline battles in eastern Ukraine\n'
                '• **Gaza / Israel–Hamas** — intense fighting in Gaza Strip since Oct 2023; major humanitarian crisis\n'
                '• **Sudan Civil War** — SAF vs RSF clashes since Apr 2023; one of world\'s worst displacement crises\n'
                '• **Myanmar Civil War** — military junta vs resistance forces; widespread civilian displacement\n'
                '• **Sahel Region** — ongoing jihadist insurgencies in Mali, Burkina Faso, Niger\n\n'
                '*For live data specific to any date, click **Query Data** to load real GDELT events.*'
            )

        if any(w in msg_lower for w in ['news','event','happening','recent','today','latest','current']):
            return (
                '## 📰 To Get Live News Analysis\n'
                '• Click **Query Data** at the top of the dashboard\n'
                '• Select a date — GDELT will fetch real event data from that day\n'
                '• Then ask me anything: top countries, conflicts, stability scores, briefings\n\n'
                '**I can analyse from loaded data:**\n'
                '• Most active countries by event count\n'
                '• Goldstein stability / conflict index\n'
                '• Event type and domain breakdowns\n'
                '• Full intelligence briefings'
            )

        return (
            '## 📡 NewsOrbit AI Assistant\n'
            'No GDELT data is loaded yet. Click **Query Data** and select a date to load live events.\n\n'
            '**I can already answer general questions like:**\n'
            '• *What major conflicts are happening?*\n'
            '• *Which regions are most unstable?*\n'
            '• *What is the Goldstein scale?*\n\n'
            'Once data is loaded I\'ll give you real-time analysis from GDELT\'s global event database.'
        )

    parts = []

    # Conflict / events / news / briefing
    if any(w in msg for w in ['conflict','war','attack','crisis','major','happening','event','news','brief','summary','overview','what']):
        parts += [
            f'## 🌍 Intelligence Briefing — {date}',
            f'• **{total:,}** geopolitical events recorded',
            fmt_stability(),
            '',
            '**Most active countries:**',
            fmt_countries(),
        ]
        if domains:
            parts += ['', '**Top news sources:**', fmt_domains()]

    # Countries
    elif any(w in msg for w in ['countr','nation','where','top','active','most']):
        parts += [f'## 🗺️ Most Active Countries — {date}', fmt_countries()]

    # Stability / Goldstein
    elif any(w in msg for w in ['stable','stability','tension','goldstein','risk','dangerous','peace','safe']):
        parts += ['## 📊 Stability Index', fmt_stability(), '', '**Countries by activity:**', fmt_countries()]

    # Count / numbers
    elif any(w in msg for w in ['how many','total','count','number','record']):
        parts += [f'## 📈 Event Count', f'• **{total:,}** GDELT records for {date}']

    # Sources / domains
    elif any(w in msg for w in ['source','website','domain','media','outlet','news site']):
        if domains:
            parts += [f'## 📰 Top News Sources — {date}', fmt_domains()]
        else:
            parts += ['## 📰 News Sources', '• No source data available']

    # Default — full snapshot
    else:
        parts += [
            f'## 📡 GDELT Snapshot — {date}',
            f'• **{total:,}** events recorded',
            fmt_stability(),
            '',
            '**Top countries:**',
            fmt_countries(),
        ]

    return '\n'.join(parts)

def _call_gemini(payload_bytes, timeout=25):
    """Try each model; return (text, None) on success or (None, err_tuple) on failure."""
    global _ai_quota_exhausted_until
    import urllib.request, urllib.error, json as _json
    last_err = None
    for model in GEMINI_MODELS:
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{model}:generateContent?key={GEMINI_API_KEY}")
        try:
            req = urllib.request.Request(url, data=payload_bytes, method='POST')
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                result = _json.loads(resp.read().decode('utf-8'))
            text = result['candidates'][0]['content']['parts'][0]['text']
            _ai_call_times.append(_time.time())
            return text, None
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8')
            print(f"Gemini {model}: HTTP {e.code} — {body[:120]}", file=sys.stderr)
            if e.code == 429:
                # If the message says "exceeded your current quota" → daily quota gone
                if 'exceeded' in body.lower() or 'quota' in body.lower():
                    _ai_quota_exhausted_until = _time.time() + 3600  # skip for 1 hour
                    print("Gemini: daily quota exhausted — disabling for 1 h", file=sys.stderr)
                last_err = ('rate_limit', e.code, body)
            elif e.code == 404:
                last_err = ('api_error', e.code, f'Model {model} not found')
            else:
                last_err = ('api_error', e.code, body[:200])
        except Exception as ex:
            last_err = ('error', 0, str(ex))
    return None, last_err


@app.route('/api/ai-chat', methods=['POST'])
@login_required
def ai_chat():
    """AI chat — uses Gemini when available, local GDELT analysis as fallback."""
    import json as _json
    try:
        data = request.json or {}
        user_message = (data.get('message') or '').strip()
        context  = data.get('context', '')
        language = data.get('language', 'en')

        if not user_message:
            return jsonify({'reply': 'Please type a question!'}), 200

        # Parse context
        ctx_obj = {}
        try:
            ctx_obj = _json.loads(context) if context else {}
        except Exception:
            pass
        slim = {
            'date':         ctx_obj.get('query_date', ''),
            'total_records':ctx_obj.get('total_records', 0),
            'top_countries':dict(list(ctx_obj.get('top_countries', {}).items())[:6]),
            'goldstein_avg':ctx_obj.get('goldstein_avg'),
            'top_domains':  dict(list(ctx_obj.get('saved_domains', {}).items())[:5]),
        }
        context_str = _json.dumps(slim)

        # 1. Cache lookup
        key = _cache_key(user_message, context_str, language)
        now = _time.time()
        if key in _ai_cache and (now - _ai_cache[key]['ts']) < _AI_CACHE_TTL:
            return jsonify({'reply': _ai_cache[key]['reply']})

        no_gdelt_data = (slim.get('total_records', 0) == 0 and not slim.get('top_countries'))

        # 2. Try Gemini (always — even without loaded data; Gemini knows global events)
        use_gemini = _gemini_available() and _rpm_ok()

        if use_gemini:
            lang_names = {
                'hi':'Hindi','ta':'Tamil','te':'Telugu','kn':'Kannada',
                'ml':'Malayalam','mr':'Marathi','bn':'Bengali','gu':'Gujarati',
                'pa':'Punjabi','ur':'Urdu','fr':'French','de':'German',
                'es':'Spanish','pt':'Portuguese','ar':'Arabic','zh':'Chinese',
                'ja':'Japanese','ko':'Korean','ru':'Russian','tr':'Turkish',
            }
            lang_instr = (f" Respond in {lang_names.get(language, language)}."
                          if language and language != 'en' else "")

            if no_gdelt_data:
                # No GDELT context — ask Gemini from general knowledge
                full_prompt = (
                    f"You are NewsOrbit AI, an expert intelligence analyst.{lang_instr} "
                    "Answer the user's question from your general knowledge about current world events. "
                    "Be concise — 4-6 bullet points.\n"
                    f"Q: {user_message}"
                )
            else:
                full_prompt = (
                    f"You are NewsOrbit AI, an expert intelligence analyst.{lang_instr} "
                    "Be concise — 3-5 bullet points max.\n"
                    f"DATA: {context_str}\nQ: {user_message}"
                )
            payload = _json.dumps({
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"temperature": 0.4, "maxOutputTokens": 250}
            }).encode('utf-8')

            text, err = _call_gemini(payload)
            if text:
                _ai_cache[key] = {'reply': text, 'ts': _time.time()}
                if len(_ai_cache) > 80:
                    oldest = sorted(_ai_cache.items(), key=lambda x: x[1]['ts'])[:20]
                    for k, _ in oldest:
                        del _ai_cache[k]
                return jsonify({'reply': text})

        # 3. Local fallback — always works
        reply = _local_answer(user_message, slim)
        _ai_cache[key] = {'reply': reply, 'ts': _time.time()}
        return jsonify({'reply': reply})

    except Exception as ex:
        print(f"ai_chat error: {ex}", file=sys.stderr)
        return jsonify({'reply': '## NewsOrbit AI\nSomething went wrong internally. Please try again.'}), 200


if __name__ == '__main__':
    # Fix multiprocessing on Windows
    import multiprocessing
    multiprocessing.freeze_support()
    
    print("="*80)
    print("🌍 GDELT PyR Web Dashboard Starting...")
    print("="*80)
    print("\n📡 Server will be available at: http://localhost:5000")
    print("📊 Open your browser and navigate to the URL above")
    print("\nPress CTRL+C to stop the server\n")
    print("="*80)
    
    # Use threaded mode instead of debug mode to avoid multiprocessing issues
    app.run(debug=False, host='127.0.0.1', port=5000, threaded=True)

    
    app.run(debug=True, host='0.0.0.0', port=5000)
