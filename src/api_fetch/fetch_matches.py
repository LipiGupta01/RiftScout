"""
This script processes pre-downloaded GRID-compatible match data and saves a normalized version for offline analysis.
"""

import os
import json
import pandas as pd
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURABLE PARAMETERS ---
# GRID API Configuration
GRID_API_KEY = os.getenv("GRID_API_KEY")
GRID_END_STATE_URL = "https://api.grid.gg/file-download/end-state/grid/series/{series_id}"

# Path to the directory for raw match data
RAW_DATA_DIR = os.path.join("data", "raw")

# Path to the pre-downloaded GRID-compatible raw data file (JSON or CSV)
INPUT_RAW_FILE = os.path.join("data", "raw_matches.json")

# Path where the discovered series IDs are stored
SERIES_IDS_FILE = os.path.join("data", "series_ids.json")

# Path where the normalized data will be saved
OUTPUT_FILE = os.path.join("data", "sample_matches.csv")

# Limit for series to process to keep demo fast
SERIES_LIMIT = 5

# Required fields for validation (aligns with typical GRID historical exports)
# These fields are expected in GRID-compatible data files for League of Legends.
REQUIRED_FIELDS = [
    'match_id',      # Unique identifier for the match (from series_id + game index)
    'team_id',       # Identifier for the team
    'team_name',     # Name of the team
    'player_name',   # Name of the player
    'role',          # Role of the player (inferred from order if not explicit)
    'champion',      # Champion played
    'win',           # Boolean indicating if the team won
    'game_duration', # Duration of the game in seconds
    'first_dragon',  # Boolean indicating if the team took the first dragon
    'first_tower',   # Boolean indicating if the team took the first tower
]

def parse_end_state_json(file_path):
    """
    Parses a GRID end-state JSON file and extracts normalized match data.
    """
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        series_state = data.get('seriesState', {})
        series_id = os.path.basename(file_path).replace('series_', '').replace('.json', '')
        games = series_state.get('games', [])
        
        # Player ID to Name mapping
        player_map = {}
        for p in series_state.get('players', []):
            p_id = p.get('id')
            p_name = p.get('name')
            if p_id and p_name:
                player_map[p_id] = p_name

        all_game_data = []

        for game_idx, game in enumerate(games):
            match_id = f"{series_id}_G{game_idx + 1}"
            duration = game.get('clock', {}).get('currentSeconds', 0)
            
            for team in game.get('teams', []):
                team_id = team.get('id')
                team_name = team.get('name')
                won = team.get('won', False)
                
                # Objectives
                objectives = team.get('objectives', [])
                first_dragon = any(obj.get('type') == 'slayDragon' and obj.get('completedFirst') for obj in objectives)
                first_tower = any(obj.get('type') == 'destroyTurret' and obj.get('completedFirst') for obj in objectives)
                
                # Fallback for tower if destroyTurret isn't exactly the key
                if not first_tower:
                    first_tower = any('Turret' in obj.get('type', '') and obj.get('completedFirst') for obj in objectives)

                # Players
                players = team.get('players', [])
                # Common roles in order for LoL
                roles_order = ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']
                
                for p_idx, player in enumerate(players):
                    p_id = player.get('id')
                    p_name = player_map.get(p_id, f"Player_{p_id}")
                    champion = player.get('character', {}).get('name', 'Unknown')
                    
                    # Infer role if not provided in JSON (GRID often orders them Top->Support)
                    role = roles_order[p_idx] if p_idx < len(roles_order) else 'UNKNOWN'
                    
                    all_game_data.append({
                        'match_id': match_id,
                        'team_id': team_id,
                        'team_name': team_name,
                        'player_name': p_name,
                        'role': role,
                        'champion': champion,
                        'win': 1 if won else 0,
                        'game_duration': duration,
                        'first_dragon': 1 if first_dragon else 0,
                        'first_tower': 1 if first_tower else 0
                    })
                    
        return pd.DataFrame(all_game_data)
        
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None
# -------------------------------

def load_series_ids(file_path):
    """
    Loads series IDs from a JSON file.
    """
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r') as f:
        series_data = json.load(f)
        # Extract IDs from the list of series objects
        return [s.get('id') for s in series_data if s.get('id')]

def download_series_end_state(series_id):
    """
    Downloads the end-state data for a specific series from the GRID API.
    """
    if not GRID_API_KEY:
        print(f"Skipping download for series {series_id}: GRID_API_KEY not found.")
        return None

    url = GRID_END_STATE_URL.format(series_id=series_id)
    headers = {"x-api-key": GRID_API_KEY}
    
    # Ensure raw data directory exists
    if not os.path.exists(RAW_DATA_DIR):
        os.makedirs(RAW_DATA_DIR)
        print(f"Created directory: {RAW_DATA_DIR}")

    output_path = os.path.join(RAW_DATA_DIR, f"series_{series_id}.json")

    try:
        print(f"Downloading end-state data for series {series_id}...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            with open(output_path, 'w') as f:
                json.dump(response.json(), f, indent=4)
            print(f"Success: Saved series {series_id} to {output_path}")
            return output_path
        else:
            print(f"Error: Failed to download series {series_id}. Status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Exception occurred while downloading series {series_id}: {e}")
        return None

def load_raw_data(file_path):
    """
    Loads raw match data from a JSON or CSV file.
    """
    if not os.path.exists(file_path):
        return None

    if file_path.endswith('.json'):
        with open(file_path, 'r') as f:
            data = json.load(f)
            # GRID data often nests matches under a 'matches' key
            if isinstance(data, dict) and 'matches' in data:
                return pd.DataFrame(data['matches'])
            return pd.DataFrame(data)
    elif file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a .json or .csv file.")

def validate_data(df):
    """
    Validates that the DataFrame contains all required fields.
    """
    missing_fields = [field for field in REQUIRED_FIELDS if field not in df.columns]
    if missing_fields:
        raise ValueError(f"Validation Error: Missing required fields: {', '.join(missing_fields)}")
    
    print(f"Success: Data validation passed. All {len(REQUIRED_FIELDS)} required fields are present.")
    return True

def normalize_matches(df):
    """
    Normalizes the match data by selecting and ordering the required fields.
    """
    # In a real scenario, this might involve more complex transformations
    # For now, we ensure the output has exactly the required fields.
    normalized_df = df[REQUIRED_FIELDS].copy()
    
    # Optional: Convert types if necessary (e.g., win to int/bool)
    # normalized_df['win'] = normalized_df['win'].astype(int)
    
    return normalized_df

def save_dataframe_to_csv(df, filepath):
    """
    Saves the pandas DataFrame to a CSV file.
    Ensures the directory exists before saving.
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    
    df.to_csv(filepath, index=False)
    print(f"Success: Saved {len(df)} normalized matches to {filepath}")

def generate_synthetic_data():
    """
    Generates a small synthetic dataset matching the GRID-compatible schema.
    Used as a fallback for development and demo purposes.
    """
    print("Generating synthetic demo data...")
    synthetic_data = [
        {
            'match_id': 'SYNTH-001_G1',
            'team_id': 'BLUE_TEAM',
            'team_name': 'Blue Warriors',
            'player_name': 'Player_1',
            'role': 'TOP',
            'champion': 'Garen',
            'win': 1,
            'game_duration': 1800,
            'first_dragon': 1,
            'first_tower': 0
        },
        {
            'match_id': 'SYNTH-001_G1',
            'team_id': 'RED_TEAM',
            'team_name': 'Red Raiders',
            'player_name': 'Player_6',
            'role': 'TOP',
            'champion': 'Darius',
            'win': 0,
            'game_duration': 1800,
            'first_dragon': 0,
            'first_tower': 1
        }
    ]
    return pd.DataFrame(synthetic_data)

if __name__ == "__main__":
    print(f"--- GRID Data Processor ---")

    df_to_process = None

    try:
        # 1. Check for discovered series IDs
        print(f"Checking for discovered series IDs in: {SERIES_IDS_FILE}...")
        series_ids = load_series_ids(SERIES_IDS_FILE)

        if series_ids:
            num_to_process = min(len(series_ids), SERIES_LIMIT)
            print(f"Found {len(series_ids)} series IDs. Processing the first {num_to_process}...")
            
            downloaded_files = []
            for i in range(num_to_process):
                series_id = series_ids[i]
                file_path = download_series_end_state(series_id)
                if file_path:
                    downloaded_files.append(file_path)

            if downloaded_files:
                print("\n--- Download Summary ---")
                print(f"Successfully saved {len(downloaded_files)} series files:")
                for path in downloaded_files:
                    print(f" - {path}")
                print("------------------------\n")

                # 2. Parse downloaded files
                print("Parsing downloaded end-state files...")
                all_dfs = []
                for path in downloaded_files:
                    df_parsed = parse_end_state_json(path)
                    if df_parsed is not None and not df_parsed.empty:
                        all_dfs.append(df_parsed)
                
                if all_dfs:
                    df_to_process = pd.concat(all_dfs, ignore_index=True)
                    print(f"Successfully parsed {len(all_dfs)} files, total {len(df_to_process)} player-match rows.")
                else:
                    print("Warning: Could not parse any of the downloaded files.")
            else:
                print("Note: No series data was downloaded.")
        else:
            print(f"Warning: No series IDs found. Run 'src/api_fetch/discover_series.py' first.")
        
        # 3. Use synthetic data if no valid data was loaded
        if df_to_process is None:
            print("Falling back to synthetic data generation...")
            df_to_process = generate_synthetic_data()

        # 4. Validate data
        print("Validating required fields...")
        validate_data(df_to_process)

        # 5. Normalize data
        print("Normalizing data...")
        df_normalized = normalize_matches(df_to_process)

        # 6. Save to CSV
        print(f"Saving normalized data to {OUTPUT_FILE}...")
        save_dataframe_to_csv(df_normalized, OUTPUT_FILE)
        
        print("\nSUCCESS: Process completed successfully.")
        print(f"A valid '{OUTPUT_FILE}' has been generated and is ready for analysis.")

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        print("The process could not be completed.")
