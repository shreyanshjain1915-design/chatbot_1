sessions = {}

def get_session(session_id):

    if session_id not in sessions:
        sessions[session_id] = {
            "chat_history": [],
            "business_type": None,
            "website_goal": None,
            "pages_needed": None,
            "tech_stack": None,
            "design_style": None
        }

    return sessions[session_id]