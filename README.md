# RiftScout 
# League of Legends Scouting Report Generator
*Submission for Sky’s the Limit — Cloud9 x JetBrains Hackathon (Category 2: Automated Scouting Report Generator)*

**Turn raw match data into actionable pre-match briefings in seconds.**

## Quick Demo
Run the full pipeline to generate a scouting report from GRID data:
```powershell
python src/api_fetch/discover_series.py    # Discover recent series
python src/api_fetch/fetch_matches.py       # Download end-state data
python main.py                              # Generate scouting report
```

## Purpose
The League of Legends Scouting Report Generator is a high-performance tool built for esports coaches and analysts. It eliminates manual VOD review and spreadsheet grind by automatically distilling complex match history into tactical briefings. By identifying opponent habits, comfort picks, and strategic weaknesses, it gives teams a decisive edge in the drafting phase and on the Rift.

## Why This Matters for Coaches
In professional League of Legends, preparation is everything. This tool reduces hours of analyst prep into a 2-minute briefing, allowing coaches to:
- **Exploit Opponent Habits**: Instantly see which lanes are vulnerable and which champions need to be banned.
- **Master the Draft**: Understand the opponent's preferred team archetypes and win conditions.
- **Speed up Workflow**: Transition from raw data to a complete scouting report in under 2 minutes.

## Category 2 Requirements Coverage
- **Team-wide strategies**: Analyzes objective control rates (Dragon/Tower) and game-phase win tendencies.
- **Player tendencies**: Tracks comfort picks, win rates per champion, and generates specific lane alerts.
- **Compositions**: Automatically classifies team comps into archetypes (e.g., Heavy Engage, Early Skirmish) with specific break points.
- **How-to-win insights**: Provides prioritized strategic recommendations based on statistical performance.

## Architecture & Data Collection
The tool uses a modular pipeline designed for stability and speed:
- **Modular Pipeline**: Clean separation between data ingestion (`src/api_fetch/`), normalization, and analysis (`src/analysis/`).
- **Official GRID Data**: Leverages GRID’s Open Platform for series discovery and fetches official end-state data for high-fidelity analysis.
- **Offline Caching**: All data is cached locally (JSON/CSV) to ensure the tool remains functional and reproducible even without an active API connection.

## Example Output
```text
--- [ LANE CHECKS ] ---
  !!! MID LANE ALERT: HIGH PRIORITY !!!
  Target: Neeko (3 games, 100.00% WR)
  Action: DENY COMFORT PICK

--- [ COMP READ ] ---
  Archetype: EARLY SKIRMISH
  - Plan:    CRUSH LANES EARLY. INVADE AND SNOWBALL TEMPO.
  - Break:   FALLS OFF IF GAME STALLS PAST 25 MINS.
  - Core:    Ambessa, Galio, Lucian, Rakan, Wukong

--- [ HOW TO BEAT THEM ] ---
[HIGH PRIORITY] PRESS THE ADVANTAGE. DON'T LET THEM BREATHE.
  Intel: Maintain pressure (50.00% overall win rate).
```

## Insights Provided
The tool produces an aggressive, coach-facing report using official GRID intel:
- **LANE CHECKS**: Priority-tagged alerts (HIGH/MEDIUM/LOW) for each lane based on opponent comfort.
- **COMP READ**: Strategic breakdown of team archetypes with clear win conditions and break points.
- **OBJECTIVE CONTROL**: Critical early-game macro patterns for Dragon and Tower control.
- **HOW TO BEAT THEM**: Direct tactical instructions categorized by priority.

## How to Run
### 1. Setup Environment
```powershell
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file in the root directory and add your GRID API Key:
```env
GRID_API_KEY=your_api_key_here
```

### 3. Run Pipeline
Execute the scripts in order:
1. **Discover Series**: `python src/api_fetch/discover_series.py` (Caches series IDs in `data/series_ids.json`)
2. **Download Data**: `python src/api_fetch/fetch_matches.py` (Downloads end-state data and generates `data/sample_matches.csv`)
3. **Generate Report**: `python main.py`

## Built with JetBrains + Junie
This project was accelerated using **IntelliJ IDEA** and **JetBrains Junie**. These tools were used to:
- **Scaffold**: Quickly generate the modular architecture and data models.
- **Refactor**: Iteratively improve the analysis logic and ensure clean code separation.
- **Accelerate**: Rapidly integrate with GRID APIs and automate the scouting workflow.

## Future Improvements
- **Opponent Filtering**: Narrow down scouting to specific teams or players.
- **Draft/Bans Integration**: Real-time drafting recommendations based on report findings.
- **Streamlit Dashboard**: A visual interface for easier consumption of insights.
- **Macro Pattern Extraction**: Deeper analysis of rotation patterns and jungle pathing.
