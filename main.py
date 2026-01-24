"""
Entry-point script for the League of Legends Scouting Report Generator.
This script coordinates the data loading, analysis, and insight generation processes to produce a final report.
"""

import sys
import os
from src.data_loading.loader import load_matches
from src.analysis.team_tendencies import analyze_team_tendencies
from src.analysis.player_tendencies import analyze_player_tendencies
from src.analysis.compositions import analyze_compositions
from src.insights.how_to_win import generate_how_to_win_insights

def main():
    """
    Main execution function for the scouting report generator.
    """
    print("="*50)
    print("League of Legends Scouting Report Generator")
    print("="*50)

    # 1. Load data
    filepath = "data/sample_matches.csv"
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found. Please ensure match data is available.")
        return

    try:
        df = load_matches(filepath)
        print(f"Successfully loaded {len(df)} rows of match data.\n")
    except Exception as e:
        print(f"Error loading match data: {e}")
        return

    # 2. Perform analysis
    print("--- [ LANE CHECKS ] ---")
    
    # Player Tendencies
    player_metrics = analyze_player_tendencies(df)
    if not player_metrics:
        print("  Player-level tendencies unavailable for this dataset.")
    else:
        for role, data in player_metrics.items():
            prefix = "!!!" if data['priority'] == "HIGH" else ">>>"
            suffix = "!!!" if data['priority'] == "HIGH" else "<<<"
            print(f"  {prefix} {role.upper()} LANE ALERT: {data['priority']} PRIORITY {suffix}")
            print(f"  Target: {data['most_played_champion']} ({data['count']} games, {data['win_rate']:.2%} WR)")
            print(f"  Action: {data['action']}")
            print("")

    # Team Tendencies
    team_metrics = analyze_team_tendencies(df)
    print("--- [ OBJECTIVE CONTROL ] ---")
    print(f"  First Dragon: {team_metrics['first_dragon_rate']:.2%}")
    print(f"  First Tower:  {team_metrics['first_tower_rate']:.2%}")
    print(f"  Win Phase:    {team_metrics['win_tendency'].upper()} GAME")
    print(f"  Early WR:     {team_metrics['early_game_win_rate']:.2%}")
    print(f"  Late WR:      {team_metrics['late_game_win_rate']:.2%}")

    # Compositions
    comp_results = analyze_compositions(df)
    print("\n--- [ COMP READ ] ---")
    if not comp_results.get('common_compositions'):
        print("  Composition patterns unavailable for this dataset.")
    else:
        for comp_data in comp_results['common_compositions']:
            comp_str = ", ".join(comp_data['composition'])
            print(f"  Archetype: {comp_data['category']}")
            print(f"  - Plan:    {comp_data['win_condition']}")
            print(f"  - Break:   {comp_data['break_point']}")
            print(f"  - Core:    {comp_str}")
            print("-" * 20)

    # 3. Generate insights
    insights = generate_how_to_win_insights(df)
    print("\n" + "="*50)
    print("--- [ HOW TO BEAT THEM ] ---")
    print("="*50)
    for insight in insights:
        print(f"\n[{insight['priority']} PRIORITY] {insight['recommendation']}")
        print(f"  Intel: {insight['metric']}")

    print("\n" + "="*50)
    print("Scouting Report Generation Complete.")
    print("="*50)

if __name__ == "__main__":
    main()
