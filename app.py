import streamlit as st
from datetime import datetime
import os
import pandas as pd # <--- THIS WAS MISSING. IMPORT PANDAS HERE.

# Import functions from your modules
from src.data_manager import (
    load_challenges,
    load_user_data,
    save_user_data,
    add_user_entry,
    get_user_entries_as_dataframe,
    USER_DATA_FILE
)
from src.challenge_logic import get_new_challenge, get_challenge_by_id

# --- Page Configuration ---
st.set_page_config(
    page_title="Growth Mindset Challenge",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- Helper Functions ---
def initialize_app_state():
    if "all_challenges" not in st.session_state:
        st.session_state.all_challenges = load_challenges()
        if not st.session_state.all_challenges:
            st.error("CRITICAL: No challenges loaded. Please check 'data/challenges_template.json'.")
            st.stop()
    if "user_data" not in st.session_state:
        st.session_state.user_data = load_user_data()
    if "current_challenge" not in st.session_state:
        assign_current_challenge()
    if "reflection_text" not in st.session_state:
        st.session_state.reflection_text = ""
    if "show_delete_confirmation" not in st.session_state:
        st.session_state.show_delete_confirmation = False

def assign_current_challenge():
    current_challenge_id = st.session_state.user_data.get("current_challenge_id")
    if current_challenge_id:
        st.session_state.current_challenge = get_challenge_by_id(
            st.session_state.all_challenges, current_challenge_id
        )
        if not st.session_state.current_challenge:
            _get_and_save_new_challenge()
    else:
        _get_and_save_new_challenge()

def _get_and_save_new_challenge():
    completed_ids = [entry["challenge_id"] for entry in st.session_state.user_data.get("completed_entries", [])]
    new_challenge = get_new_challenge(st.session_state.all_challenges, completed_ids)
    st.session_state.current_challenge = new_challenge
    if new_challenge:
        st.session_state.user_data["current_challenge_id"] = new_challenge["id"]
    else:
        st.session_state.user_data["current_challenge_id"] = None
    save_user_data(st.session_state.user_data)
    st.session_state.reflection_text = ""

def handle_challenge_completion(reflection_text):
    if reflection_text.strip():
        challenge = st.session_state.current_challenge
        add_user_entry(challenge["id"], challenge["challenge"], reflection_text.strip())
        st.success("Great job! Your reflection has been saved.")
        st.session_state.user_data = load_user_data()
        _get_and_save_new_challenge()
        st.rerun()
    else:
        st.warning("Please write a reflection before saving.")

def handle_skip_challenge():
    _get_and_save_new_challenge()
    st.rerun()

def clear_all_user_data():
    st.session_state.user_data = {"completed_entries": [], "current_challenge_id": None}
    save_user_data(st.session_state.user_data)
    if os.path.exists(USER_DATA_FILE):
        try:
            os.remove(USER_DATA_FILE)
            st.sidebar.success("All user data has been cleared from the system.")
        except OSError as e:
            st.sidebar.error(f"Error deleting user data file: {e}")
    else:
        st.sidebar.success("User data cleared (no file to delete).")
    st.session_state.show_delete_confirmation = False
    assign_current_challenge()
    st.rerun()

# --- Initialize Application State ---
initialize_app_state()

# --- Main Application UI ---
st.title("✨ Growth Mindset Challenge ✨")
st.markdown(
    "Embrace challenges, persist through obstacles, learn from criticism, "
    "and find inspiration in the success of others."
)
st.divider()

if st.session_state.current_challenge:
    challenge = st.session_state.current_challenge
    st.subheader("Today's Challenge:")
    st.info(f"**{challenge['challenge']}** (Category: {challenge.get('category', 'General')})")
    with st.form(key="reflection_form"):
        reflection_input = st.text_area(
            "Your reflection on this challenge:",
            value=st.session_state.reflection_text,
            height=150,
            key="reflection_input_area"
        )
        st.session_state.reflection_text = reflection_input
        submitted = st.form_submit_button("✅ Mark as Completed & Save", type="primary", use_container_width=True)
        if submitted:
            handle_challenge_completion(reflection_input)
    if st.button("🔄 Get a Different Challenge", use_container_width=True, key="skip_button"):
        handle_skip_challenge()
else:
    st.success("🎉 You've completed all available challenges! Well done!")
    if st.button("Reset and Start Over? (Deletes Progress)", key="reset_all_challenges_button"):
        st.session_state.show_delete_confirmation = True
        st.rerun()

st.divider()

st.subheader("📝 Your Growth Journey (Past Reflections)")
entries_df = get_user_entries_as_dataframe()

if not entries_df.empty:
    sort_column = "date_completed_dt" if "date_completed_dt" in entries_df.columns else "date_completed"
    if sort_column in entries_df.columns:
        try:
            entries_df[sort_column] = pd.to_datetime(entries_df[sort_column], errors='coerce')
            entries_df = entries_df.sort_values(by=sort_column, ascending=False)
        except Exception:
            st.warning("Could not reliably sort entries by date.")

    display_df = pd.DataFrame() # Initialize an empty DataFrame
    if "date_completed_dt" in entries_df.columns and not entries_df["date_completed_dt"].isnull().all():
        display_df["Date"] = entries_df["date_completed_dt"].dt.strftime('%Y-%m-%d %H:%M')
    elif "date_completed" in entries_df.columns:
         display_df["Date"] = entries_df["date_completed"]

    if "challenge_text" in entries_df.columns:
        display_df["Challenge"] = entries_df["challenge_text"]
    if "reflection" in entries_df.columns:
        display_df["Your Reflection"] = entries_df["reflection"]

    if not display_df.empty:
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.write("No reflections to display in table format.")
else:
    st.write("No reflections saved yet. Complete your first challenge!")

st.sidebar.header("About")
st.sidebar.info(
    "This app helps you cultivate a growth mindset by providing daily challenges "
    "and a space to reflect on your progress."
)
st.sidebar.markdown("---")
st.sidebar.header("Settings")
if st.sidebar.button("Clear All My Data (Careful!)", key="sidebar_delete_button"):
    st.session_state.show_delete_confirmation = True

if st.session_state.show_delete_confirmation:
    st.sidebar.warning("ARE YOU SURE you want to delete all your data? This cannot be undone.")
    col1_sidebar, col2_sidebar = st.sidebar.columns(2)
    with col1_sidebar:
        if st.button("YES, Delete All", type="primary", key="confirm_delete_yes"):
            clear_all_user_data()
    with col2_sidebar:
        if st.button("NO, Keep Data", key="confirm_delete_no"):
            st.session_state.show_delete_confirmation = False
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("Made by **Taha**") # <--- CHANGED HERE