"""
This module contains functions for analyzing team-wide tendencies in League of Legends matches.
"""
import pandas as pd

def analyze_team_tendencies(df: pd.DataFrame) -> dict:
    """
    Analyzes team tendencies from match data.

    Calculates:
    - First dragon contest rate
    - First tower rate
    - Early vs late game win tendency

    Args:
        df (pd.DataFrame): DataFrame containing match data. 
                           Expected columns: 'first_dragon', 'first_tower', 'game_duration', 'win'

    Returns:
        dict: A dictionary containing the calculated metrics.
    """
    # Initialize the results dictionary
    results = {}

    # 1. First Dragon Contest Rate
    # Assuming 'first_dragon' is a boolean or 1/0 indicating if the team got the first dragon.
    # If the data represents a single team's perspective across multiple games:
    first_dragon_rate = df['first_dragon'].mean()
    results['first_dragon_rate'] = float(first_dragon_rate)

    # 2. First Tower Rate
    # Assuming 'first_tower' is a boolean or 1/0 indicating if the team got the first tower.
    first_tower_rate = df['first_tower'].mean()
    results['first_tower_rate'] = float(first_tower_rate)

    # 3. Early vs Late Game Win Tendency
    # Reasoning: We split at 30 minutes (1800 seconds) because this is typically 
    # when many champions reach their 3-item power spikes and the game transitions 
    # to late-game macro.
    early_game_mask = df['game_duration'] < 1800
    late_game_mask = df['game_duration'] >= 1800

    early_win_rate = df[early_game_mask]['win'].mean() if not df[early_game_mask].empty else 0.0
    late_win_rate = df[late_game_mask]['win'].mean() if not df[late_game_mask].empty else 0.0

    results['early_game_win_rate'] = float(early_win_rate)
    results['late_game_win_rate'] = float(late_win_rate)
    results['win_tendency'] = "early" if early_win_rate > late_win_rate else "late"

    return results
