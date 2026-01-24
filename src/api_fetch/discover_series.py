"""
This script queries the GRID Central Data GraphQL API to discover recent League of Legends esports series.
It retrieves series IDs and metadata which can be used for downstream data ingestion and analysis.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- GRID API Configuration ---
# The Open Platform endpoint is required for hackathon access to Central Data
GRID_OPEN_PLATFORM_URL = "https://api-op.grid.gg/central-data/graphql"
GRID_API_KEY = os.getenv("GRID_API_KEY")

# Path where the discovered series IDs will be saved
SERIES_CACHE_FILE = os.path.join("data", "series_ids.json")

# GraphQL Query to discover recent League of Legends series
# This query fetches the most recent 15 ESPORTS series for LoL (title ID 3)
# Note: Ordering requires separate enum values for orderBy and orderDirection.
SERIES_DISCOVERY_QUERY = """
query GetRecentSeries {
  allSeries(
    filter: { titleIds: { in: ["3"] }, types: [ESPORTS] }
    orderBy: StartTimeScheduled
    orderDirection: DESC
    first: 15
  ) {
    edges {
      node {
        id
        tournament {
          name
        }
      }
    }
  }
}
"""

def discover_series():
    """
    Queries the GRID GraphQL API for recent series.
    """
    if not GRID_API_KEY:
        print("Error: GRID_API_KEY not found in environment variables.")
        return None

    headers = {
        "Content-Type": "application/json",
        "x-api-key": GRID_API_KEY
    }

    payload = {
        "query": SERIES_DISCOVERY_QUERY
    }

    try:
        print(f"Querying GRID Central Data API for recent series...")
        response = requests.post(GRID_OPEN_PLATFORM_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if "errors" in data:
            print("\nGraphQL Validation Errors:")
            for error in data["errors"]:
                print(f" - {error.get('message', 'Unknown error')}")
            return None
            
        print("Success: Central Data access via the Open Platform endpoint is working.")
        series_edges = data.get("data", {}).get("allSeries", {}).get("edges", [])
        return [edge.get("node") for edge in series_edges if edge.get("node")]

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 400:
            print("\nBad Request: The server could not process the request.")
            try:
                error_details = response.json()
                if "errors" in error_details:
                    print("GraphQL Validation Errors:")
                    for error in error_details["errors"]:
                        print(f" - {error.get('message', 'Unknown error')}")
                else:
                    print(f"Details: {error_details}")
            except:
                print(f"HTTP Error: {http_err}")
        elif response.status_code == 401:
            print("\nAuthentication Error: Invalid GRID API Key. Please check your .env file.")
        elif response.status_code == 404:
            print("\nError: GRID GraphQL endpoint not found. Please verify the URL.")
        else:
            print(f"\nHTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
    
    return None

def save_series_to_json(series_list, filepath):
    """
    Saves the list of discovered series to a JSON file.
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    try:
        with open(filepath, 'w') as f:
            json.dump(series_list, f, indent=4)
        print(f"\nSuccess: Saved {len(series_list)} series to {filepath}")
    except Exception as e:
        print(f"\nError saving series to JSON: {e}")

if __name__ == "__main__":
    print("--- GRID Series Discovery ---")
    
    series_list = discover_series()
    
    if series_list:
        print(f"Successfully discovered {len(series_list)} recent series:\n")
        
        # Header
        header_id = "Series ID"
        header_tournament = "Tournament Name"
        print(f"{header_id:<40} | {header_tournament}")
        print("-" * 80)
        
        for series in series_list:
            series_id = series.get('id', 'Unknown ID')
            tournament = series.get('tournament', {})
            tournament_name = tournament.get('name', 'Unknown Tournament') if tournament else 'Unknown Tournament'
            
            print(f"{series_id:<40} | {tournament_name}")
        
        # Save to local JSON file
        save_series_to_json(series_list, SERIES_CACHE_FILE)
    else:
        print("\nNo series data retrieved.")
        print("Note: Ensure your GRID_API_KEY is valid and you have access to Central Data.")
