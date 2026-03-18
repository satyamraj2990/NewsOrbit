# 🌍 NewsOrbit

## Global Intelligence Platform

This is a modern, interactive intelligence platform for exploring global events data visually.

## 🚀 Quick Start

### Option 1: Windows Batch File
```bash
start_dashboard.bat
```

### Option 2: PowerShell
```powershell
.\start_dashboard.ps1
```

### Option 3: Manual
```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

## ✨ Features

### 📊 **Real-Time Data Visualization**
- Interactive statistics cards
- Top countries analysis
- Actor identification
- Event category breakdown
- Goldstein tone analysis

### 🎨 **Beautiful UI**
- Modern gradient design
- Responsive layout
- Smooth animations
- Professional presentation style
- Color-coded data cards

### 🔍 **Interactive Queries**
- Date selection
- Table switching (Events, GKG, Mentions)
- Version selection (GDELT 1.0 / 2.0)
- Real-time data fetching
- Error handling

### 📈 **Data Analysis**
- Top 10 countries
- Top 10 actors
- Event distribution
- Sample event details
- Statistical summaries

## 🎯 Perfect for Presentations

This dashboard is designed to impress:
- ✅ Clean, professional interface
- ✅ Live data from GDELT servers
- ✅ Easy to navigate
- ✅ Visually appealing
- ✅ Responsive design

## 📱 Screenshots

The dashboard includes:
- **Header**: Beautiful gradient banner with project title
- **Controls**: Easy date/table/version selection
- **Stats Cards**: 4 key metrics at a glance
- **Data Sections**: Organized lists of top countries, actors, events
- **Sample Events**: Detailed event information

## 🛠️ Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Data**: GDELT PyR library (gdeltPyR)
- **Styling**: Custom CSS with gradients and animations

## 🌟 API Endpoints

- `GET /` - Main dashboard
- `POST /api/query` - Query GDELT data
- `GET /api/stats/<table>` - Get table statistics
- `GET /api/schema/<table>` - Get table schema
- `GET /api/quick-query` - Quick overview

## 💡 Tips for Presentations

1. **Start the server** before your presentation
2. **Test the connection** by loading http://localhost:5000
3. **Prepare sample queries** ahead of time
4. **Explain the visualizations** as they load
5. **Highlight the real-time data** capability

## 🎨 Customization

You can customize the colors in `templates/index.html`:
- Primary color: `#667eea`
- Secondary color: `#764ba2`
- Background gradients
- Card shadows

## 📞 Support

The dashboard automatically:
- Shows loading indicators
- Handles errors gracefully
- Displays helpful messages
- Auto-loads data on startup

## 🏆 What Makes This Great

✨ **Professional Design** - Looks polished and modern
📊 **Real Data** - Live queries to GDELT servers
🎯 **Easy to Use** - Intuitive interface
🚀 **Fast Loading** - Optimized performance
📱 **Responsive** - Works on different screen sizes

---

**Ready to present? Run the dashboard and impress your audience!** 🌍
