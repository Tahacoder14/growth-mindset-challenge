import random

def get_new_challenge(all_challenges, completed_challenge_ids):
    """
    Gets a new challenge that the user hasn't completed yet.
    Returns a challenge dictionary or None if all are completed or no challenges exist.
    """
    if not all_challenges:
        return None

    available_challenges = [
        ch for ch in all_challenges if ch["id"] not in completed_challenge_ids
    ]

    if not available_challenges:
        return None # All challenges completed

    return random.choice(available_challenges)

def get_challenge_by_id(all_challenges, challenge_id):
    """Gets a challenge by its ID."""
    if challenge_id is None:
        return None
    for ch in all_challenges:
        if ch["id"] == challenge_id:
            return ch
    return None