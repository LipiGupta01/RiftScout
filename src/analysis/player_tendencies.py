"""
This module contains functions for analyzing player-specific tendencies in League of Legends matches.
"""
import pandas as pd

def analyze_player_tendencies(df: pd.DataFrame, roles: list = None) -> dict:
    """
    Identifies the most played champion and their win rate per selected role.

    Args:
        df (pd.DataFrame): DataFrame containing match data.
                           Expected columns: 'role', 'champion', 'win'
        roles (list, optional): List of roles to analyze. If None, analyzes all roles in df.

    Returns:
        dict: A dictionary where keys are roles and values are dictionaries containing
              'most_played_champion' and 'win_rate'.
    """
    # Assumption: 'win' column is numeric (1 for win, 0 for loss) or boolean.
    # Assumption: 'role' and 'champion' columns exist and contain string identifiers.

    if 'role' not in df.columns or 'champion' not in df.columns:
        # Return an empty result indicating that player-level role analysis is unavailable
        return {}

    if roles:
        df = df[df['role'].isin(roles)]

    results = {}

    # Group by role to find tendencies for each role
    for role, role_df in df.groupby('role'):
        if role_df.empty:
            continue
            
        # Count occurrences of each champion in this role
        champion_counts = role_df['champion'].value_counts()
        
        if champion_counts.empty:
            continue
            
        # Ignore or de-emphasize champions with very small sample sizes (e.g., less than 2 games)
        # This improves reliability by ensuring we don't report "tendencies" based on a single outlier game.
        filtered_counts = champion_counts[champion_counts >= 2]
        
        if filtered_counts.empty:
            # If no champion has 2+ games, we might still want to know the most played, 
            # but we'll mark it as low confidence if we were to extend this further.
            # For now, we strictly follow the requirement to ignore small samples.
            continue
            
        most_played_champion = filtered_counts.idxmax()
        games_played = int(filtered_counts.max())
        
        # Calculate win rate for the most played champion
        champion_df = role_df[role_df['champion'] == most_played_champion]
        win_rate = float(champion_df['win'].mean())
        
        # Determine Priority and Actionable Call
        # HIGH Priority: 3+ games AND (WR > 70% or WR < 30%)
        # MEDIUM Priority: 2+ games AND (WR > 60% or WR < 40%)
        # LOW Priority: Otherwise
        if games_played >= 3 and (win_rate >= 0.7 or win_rate <= 0.3):
            priority = "HIGH"
        elif games_played >= 2 and (win_rate >= 0.6 or win_rate <= 0.4):
            priority = "MEDIUM"
        else:
            priority = "LOW"

        # Actionable Call based on Win Rate
        if win_rate >= 0.6:
            action = "DENY COMFORT PICK"
        elif win_rate <= 0.4:
            action = "FORCE LOSING MATCHUP"
        else:
            action = "IGNORE AND PLAY CROSS-MAP"

        results[role] = {
            'most_played_champion': most_played_champion,
            'win_rate': win_rate,
            'count': games_played,
            'priority': priority,
            'action': action
        }
        
    return results
