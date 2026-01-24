"""
This module contains functions for analyzing team compositions in League of Legends matches.
"""
import pandas as pd

def analyze_compositions(df: pd.DataFrame) -> dict:
    """
    Identifies the most common team compositions and classifies them.

    Compositions are identified by grouping the champions in a team.
    Classification is done using simple rule-based logic based on a mock 
    attribute mapping for champions.

    Args:
        df (pd.DataFrame): DataFrame containing match data.
                           Expected columns: 'match_id', 'team_id', 'champion', 'win'

    Returns:
        dict: A dictionary containing most common compositions and their classifications.
    """
    if 'champion' not in df.columns:
        # Composition analysis requires player-level champion data. 
        # If missing (e.g., only match-level data is present), we return an empty result to degrade gracefully.
        return {'common_compositions': []}

    # 1. Group by match and team to get the composition
    # We assume 'df' has one row per player per match.
    # We want to represent a composition as a sorted tuple of champion names.
    
    # Ensure champions are strings for sorting. 
    # Using .loc to avoid SettingWithCopyWarning and ensuring we work with the validated column.
    df_comp = df.copy()
    df_comp['champion'] = df_comp['champion'].astype(str)
    
    # Group and aggregate champions into a sorted tuple
    compositions = df_comp.groupby(['match_id', 'team_id'])['champion'].apply(lambda x: tuple(sorted(x))).reset_index()
    compositions.rename(columns={'champion': 'composition'}, inplace=True)
    
    # Count occurrences of each composition
    comp_counts = compositions['composition'].value_counts().reset_index()
    comp_counts.columns = ['composition', 'count']
    
    # 2. Rule-based classification
    # In a real scenario, we'd have a database of champion tags (e.g., 'Assassin', 'Tank', 'Enchanter').
    # For this implementation, we'll use a simplified mapping for demonstration.
    
    champion_tags = {
        # Early Skirmish
        'Lee Sin': 'skirmish', 'Renekton': 'skirmish', 'LeBlanc': 'skirmish', 'Xin Zhao': 'skirmish', 'Elise': 'skirmish', 'Lucian': 'skirmish',
        'Nidalee': 'skirmish', 'Kindred': 'skirmish', 'Sylas': 'skirmish', 'Jayce': 'skirmish', 'Wukong': 'skirmish', 'Taliyah': 'skirmish',
        # Protect the Carry
        'Lulu': 'protect', 'Janna': 'protect', 'Braum': 'protect', 'Kog\'Maw': 'protect', 'Vayne': 'protect', 'Tahm Kench': 'protect',
        'Milio': 'protect', 'Yuumi': 'protect', 'Zilean': 'protect', 'Rakan': 'protect', 'Karma': 'protect',
        # Heavy Engage
        'Malphite': 'engage', 'Amumu': 'engage', 'Leona': 'engage', 'Nautilus': 'engage', 'Jarvan IV': 'engage', 'Ornn': 'engage', 'Galio': 'engage',
        'Vi': 'engage', 'Sejuani': 'engage', 'Sion': 'engage', 'K\'Sante': 'engage', 'Alistar': 'engage', 'Maokai': 'engage',
        # Scaling
        'Kayle': 'scaling', 'Kassadin': 'scaling', 'Jinx': 'scaling', 'Ryze': 'scaling', 'Sivir': 'scaling', 'Viktor': 'scaling',
        'Smolder': 'scaling', 'Azir': 'scaling', 'Caitlyn': 'scaling', 'Senna': 'scaling', 'Vladimir': 'scaling'
    }
    
    def classify_team_composition(comp: tuple) -> dict:
        """
        Classifies a team composition based on the count of specific champion archetypes.
        
        Logic:
        - PROTECT THE CARRY: High count of 'protect' tags (frontline/peel for ADC).
        - HEAVY ENGAGE: High count of 'engage' tags (hard CC initiators).
        - EARLY SKIRMISH: High count of 'skirmish' tags (early tempo/fighters).
        - SCALING: High count of 'scaling' tags (late game inevitability).
        """
        counts = {'skirmish': 0, 'protect': 0, 'engage': 0, 'scaling': 0}
        
        for champ in comp:
            tag = champion_tags.get(champ)
            if tag:
                counts[tag] += 1
        
        # Determine primary archetype (highest count)
        # We prioritize specific archetypes over 'standard' if they have at least 2 matching tags.
        primary_style = max(counts, key=counts.get)
        if counts[primary_style] < 2:
            primary_style = 'standard'

        archetypes = {
            'skirmish': {
                'category': 'EARLY SKIRMISH',
                'win_condition': 'CRUSH LANES EARLY. INVADE AND SNOWBALL TEMPO.',
                'break_point': 'FALLS OFF IF GAME STALLS PAST 25 MINS.'
            },
            'protect': {
                'category': 'PROTECT THE CARRY',
                'win_condition': 'PEEL FOR ADC. WIN FRONT-TO-BACK TEAMFIGHTS.',
                'break_point': 'VULNERABLE IF CARRY IS DIVED OR PICKED EARLY.'
            },
            'engage': {
                'category': 'HEAVY ENGAGE',
                'win_condition': 'FORCE 5V5. CHAIN CC ON PRIORITY TARGETS.',
                'break_point': 'USELESS IF THEY MISS INITIAL ENGAGE OR GET POKED.'
            },
            'scaling': {
                'category': 'SCALING',
                'win_condition': 'STALL FOR ITEMS. OUT-STAT IN LATE GAME CLUTCHES.',
                'break_point': 'EXTREMELY WEAK TO EARLY DIVES AND SOUL PRESSURE.'
            },
            'standard': {
                'category': 'STANDARD',
                'win_condition': 'ADAPT TO FLOW. PLAY FOR STANDARD OBJECTIVES.',
                'break_point': 'LACKS SPECIALIZED STRENGTH AGAINST FOCUSED COMPS.'
            }
        }
        
        return archetypes.get(primary_style)

    results = []
    # Take top 5 common compositions for the report
    for _, row in comp_counts.head(5).iterrows():
        comp = row['composition']
        classification = classify_team_composition(comp)
        results.append({
            'composition': list(comp),
            'count': int(row['count']),
            **classification
        })

    return {'common_compositions': results}
