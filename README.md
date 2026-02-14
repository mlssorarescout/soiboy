# ⚽ Opponent Difficulty Dashboard

A professional Streamlit dashboard for analyzing fixture difficulty across different competitions and gameweeks. Visualize opponent strength with color-coded heat maps and make data-driven decisions for fantasy sports or tactical analysis.

![Dashboard Preview](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)

## ✨ Features

- **Interactive Filtering**: Filter by competition, position, and gameweek
- **Dual Metrics**: View difficulty using mean or median scores
- **Color-Coded Visualization**: Instantly identify easy and hard fixtures
- **Responsive Grid**: Sortable, resizable columns with tooltips showing opponent names
- **CSV Export**: Download filtered data for further analysis
- **Professional UI**: Modern, clean interface with smooth animations

## 📋 Requirements

- Python 3.8 or higher
- Required packages (see `requirements.txt`)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mlssorarescout/soiboy.git
   cd soiboy
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your data file**
   - Create a `data` directory in the project root
   - Place your `Calculated Opponent Difficulty.csv` file in the `data` directory
   - Or update the `DATA_PATH` in `src/config.py` to point to your CSV file

## 🎮 Usage

Run the dashboard with:

```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

### Using the Dashboard

1. **Select a Competition**: Choose from available competitions in the sidebar
2. **Choose a Position**: Filter by player position
3. **Pick Your Metric**: Select between mean or median difficulty scores
4. **Select Gameweeks**: Choose which gameweeks to display (default: all)
5. **Analyze**: Review the color-coded grid where:
   - 🟢 Green = Easier fixtures
   - ⚪ White = Neutral fixtures
   - 🔴 Red = Harder fixtures
6. **Export**: Download the current view as CSV for offline analysis

## 📁 Project Structure

```
soiboy/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── data/                  # Data directory (create this)
│   └── Calculated Opponent Difficulty.csv
└── src/                   # Source code modules
    ├── config.py          # Configuration settings
    ├── dashboard.py       # Main dashboard logic
    ├── data.py            # Data loading and processing
    ├── grid.py            # AG Grid configuration
    ├── pivots.py          # Pivot table creation
    └── styles.py          # CSS styling
```

## ⚙️ Configuration

Edit `src/config.py` to customize:

- **Data Path**: Location of your CSV file
- **Competition Names**: Display names for competitions
- **Color Scheme**: RGB values for difficulty colors
- **Difficulty Settings**: Neutral point and color intensity

## 📊 Data Format

Your CSV file should include these columns:

- `Date`: Match date
- `Competition_Display` or `Comp_Slug`: Competition identifier
- `Position`: Player position
- `Score_mean`: Mean difficulty score
- `Score_median`: Median difficulty score
- `Domestic League Ranking`: Team ranking
- `Opponent`: Opponent team name
- `Location`: Home or Away

## 🎨 Customization

### Changing Colors

Edit the `DIFFICULTY_COLORS` dictionary in `src/config.py`:

```python
DIFFICULTY_COLORS = {
    "easy": (34, 197, 94),    # Green
    "hard": (239, 68, 68),     # Red
    "neutral": (255, 255, 255) # White
}
```

### Adjusting Difficulty Threshold

Modify the `DIFFICULTY_CENTER` value to change the neutral point:

```python
DIFFICULTY_CENTER = 48  # Adjust this value
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🐛 Troubleshooting

### Data file not found
- Ensure your CSV file is in the correct location
- Check the `DATA_PATH` setting in `src/config.py`
- Verify the file name matches exactly

### Missing dependencies
- Reinstall requirements: `pip install -r requirements.txt`
- Ensure you're using Python 3.8 or higher

### Grid not displaying
- Check browser console for JavaScript errors
- Try refreshing the page
- Ensure `allow_unsafe_jscode=True` is set in AG Grid configuration

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

Made with ⚽ for fantasy football enthusiasts and tactical analysts
