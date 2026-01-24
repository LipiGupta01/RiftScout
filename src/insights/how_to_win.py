"""
This module generates actionable insights on how to win matches based on statistical analysis.
"""
import pandas as pd

def generate_how_to_win_insights(df: pd.DataFrame) -> list:
    """
    Derives actionable recommendations based on observed statistical weaknesses in the match data.

    Args:
        df (pd.DataFrame): DataFrame containing match data.
                           Expected columns: 'first_dragon', 'first_tower', 'game_duration', 'win'

    Returns:
        list: A list of dictionaries, each containing a recommendation and the backing metric.
    """
    insights = []
    
    # 1. HIGH Priority Call: Based on Dragon Control or Late Game Falloff
    dragon_rate = df['first_dragon'].mean()
    early_game_mask = df['game_duration'] < 1800
    late_game_mask = df['game_duration'] >= 1800
    early_win_rate = df[early_game_mask]['win'].mean() if not df[early_game_mask].empty else 0.0
    late_win_rate = df[late_game_mask]['win'].mean() if not df[late_game_mask].empty else 0.0

    if dragon_rate < 0.4:
        insights.append({
            "recommendation": "FORCE DRAGON FIGHTS. DENY SOUL AT ALL COSTS.",
            "metric": f"Opponent dragon control is weak ({dragon_rate:.2%} capture rate).",
            "priority": "HIGH"
        })
    elif early_win_rate > late_win_rate + 0.15:
        insights.append({
            "recommendation": "STALL FOR LATE. PUNISH THEIR MID-GAME DESPERATION.",
            "metric": f"Massive late-game drop detected ({early_win_rate:.2%} Early vs {late_win_rate:.2%} Late WR).",
            "priority": "HIGH"
        })
    else:
        # Calculate general win rate as a concrete stat
        overall_win_rate = df['win'].mean()
        insights.append({
            "recommendation": "PRESS THE ADVANTAGE. DON'T LET THEM BREATHE.",
            "metric": f"Maintain pressure ({overall_win_rate:.2%} overall win rate).",
            "priority": "HIGH"
        })

    # 2. MEDIUM Priority Call: Based on Tower Rate or Early Weakness
    tower_rate = df['first_tower'].mean()
    if tower_rate < 0.5:
        insights.append({
            "recommendation": "CRASH WAVES. PUNISH WEAK ROTATIONS FOR PLATES.",
            "metric": f"Subpar first tower control ({tower_rate:.2%} rate).",
            "priority": "MEDIUM"
        })
    elif late_win_rate > early_win_rate + 0.1:
        insights.append({
            "recommendation": "INVADE EARLY. BREAK THEIR SCALING BEFORE IT STARTS.",
            "metric": f"Scaling threat detected ({late_win_rate:.2%} Late WR vs {early_win_rate:.2%} Early).",
            "priority": "MEDIUM"
        })
    else:
        insights.append({
            "recommendation": "CONTROL VISION. PUNISH FACE-CHECKS IN RIVER.",
            "metric": "Standard objective pacing detected.",
            "priority": "MEDIUM"
        })

    # 3. SITUATIONAL Call: Tactical advice
    insights.append({
        "recommendation": "BAIT BARON. FORCE THEM INTO A BAD FACE-CHECK.",
        "metric": "Situational tactical opening.",
        "priority": "SITUATIONAL"
    })

    return insights
