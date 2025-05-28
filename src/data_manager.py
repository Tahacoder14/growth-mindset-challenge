import json
import os
from datetime import datetime
import streamlit as st  # <--- IMPORTANT: Import Streamlit here
import pandas as pd     # <--- Import Pandas

CHALLENGES_FILE = "data/challenges_template.json"
USER_DATA_FILE = "data/user_data.json"

def load_challenges():
    """Loads challenges from the JSON file."""
    try:
        with open(CHALLENGES_FILE, 'r') as f:
            challenges = json.load(f)
        return challenges
    except FileNotFoundError:
        st.error(f"Error: The challenges file '{CHALLENGES_FILE}' was not found.")
        return []
    except json.JSONDecodeError:
        st.error(f"Error: The challenges file '{CHALLENGES_FILE}' is not a valid JSON.")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred while loading challenges: {e}")
        return []

def load_user_data():
    """Loads user data from the JSON file.
       If the file doesn't exist, returns a default structure.
    """
    if not os.path.exists(USER_DATA_FILE):
        return {"completed_entries": [], "current_challenge_id": None}
    try:
        with open(USER_DATA_FILE, 'r') as f:
            user_data = json.load(f)
        # Ensure essential keys exist
        if "completed_entries" not in user_data:
            user_data["completed_entries"] = []
        if "current_challenge_id" not in user_data:
            user_data["current_challenge_id"] = None
        return user_data
    except json.JSONDecodeError:
        st.error(f"Error: The user data file '{USER_DATA_FILE}' seems corrupted. Starting with fresh data. You might want to check or delete it manually.")
        # To prevent a loop if saving also fails, return a default and don't try to re-save here.
        return {"completed_entries": [], "current_challenge_id": None}
    except Exception as e:
        st.error(f"An unexpected error occurred while loading user data: {e}")
        return {"completed_entries": [], "current_challenge_id": None}


def save_user_data(user_data):
    """Saves user data to the JSON file."""
    try:
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(user_data, f, indent=4)
    except Exception as e:
        st.error(f"Critical Error: Could not save user data to '{USER_DATA_FILE}'. Please check permissions or disk space. Error: {e}")
        # Depending on how critical saving is, you might want to handle this more robustly.


def add_user_entry(challenge_id, challenge_text, reflection):
    """Adds a new entry to user data and saves it."""
    user_data = load_user_data() # Load current data
    entry = {
        "challenge_id": challenge_id,
        "challenge_text": challenge_text,
        "reflection": reflection,
        "date_completed": datetime.now().isoformat() # Store as ISO format string for consistency
    }
    # Ensure 'completed_entries' list exists
    if "completed_entries" not in user_data or not isinstance(user_data["completed_entries"], list):
        user_data["completed_entries"] = []

    user_data["completed_entries"].append(entry)
    save_user_data(user_data)
    return entry

# --- Pandas Integration ---
def get_user_entries_as_dataframe():
    """
    Loads user entries from user_data.json and returns them as a Pandas DataFrame.
    Includes basic date conversion.
    """
    user_data = load_user_data()
    entries = user_data.get("completed_entries", [])

    if not entries:
        return pd.DataFrame() # Return an empty DataFrame if no entries

    df = pd.DataFrame(entries)

    # Convert 'date_completed' to datetime objects for easier manipulation/sorting
    if "date_completed" in df.columns:
        try:
            df["date_completed_dt"] = pd.to_datetime(df["date_completed"])
        except Exception as e:
            st.warning(f"Could not convert all 'date_completed' strings to datetime objects: {e}")
            df["date_completed_dt"] = pd.NaT # Fill with Not a Time for unparseable
    return df

def get_challenges_as_dataframe():
    """
    Loads all challenges from challenges_template.json and returns them as a Pandas DataFrame.
    """
    challenges_list = load_challenges()
    if not challenges_list:
        return pd.DataFrame() # Return empty DataFrame if no challenges
    return pd.DataFrame(challenges_list)