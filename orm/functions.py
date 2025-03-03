import streamlit as st
import json
import hashlib
from sqlalchemy import func
from orm.models import User, Message, SessionLocal

def verify_user_credentials(username: str, password: str) -> bool:
    try:
        # Create a new database session
        session = SessionLocal()

        # Hash the password using SHA-256
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Query to check if the username and hashed password exist in the users table
        user = session.query(User).filter(func.lower(User.username) == username.lower(), User.password == hashed_password).first()
        
        st.session_state.cookies["user_id"] = json.dumps(user.id)

        # Close the database session
        session.close()

        # Return True if the user exists, otherwise return False
        return user is not None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return False
    
def change_password(user_id: int, current_password: str, new_password: str) -> bool:
    # Create a new database session
    session = SessionLocal()

     # Retrieve the existing user from the database
    user = session.query(User).filter(User.id == user_id).first()

    current_password = hashlib.sha256(current_password.encode()).hexdigest()
    
    # Verify the current password
    if user and current_password ==  user.password:
        # Retrieve the existing user from the database
        user = session.query(User).filter(User.id == user_id).first()

        # Update the user's password in the database
        user.password = hashlib.sha256(new_password.encode()).hexdigest()
        session.commit()

        # Close the session
        session.close()

        return True
    else:
        session.close()

        return False

def set_user_preferences_in_session_state():
    user_id = st.session_state.cookies.get("user_id")
    user = get_user(user_id)
    
    if "loaded" not in st.session_state:
        st.session_state.show_sql = user.show_sql
        st.session_state.show_table = user.show_table
        st.session_state.show_plotly_code = user.show_plotly_code
        st.session_state.show_chart = user.show_chart
        st.session_state.show_question_history = user.show_question_history
        st.session_state.show_summary = user.show_summary
        st.session_state.voice_input = user.voice_input
        st.session_state.speak_summary = user.speak_summary
        st.session_state.show_suggested = user.show_suggested
        st.session_state.show_followup = user.show_followup
        st.session_state.llm_fallback = user.llm_fallback
        st.session_state.min_message_id = user.min_message_id
        st.session_state.loaded = True # dont call after initial load
    
    return user

def save_user_settings():
    user_id = st.session_state.cookies.get("user_id")
    user_id = json.loads(user_id)
    
    # Create a new database session
    session = SessionLocal()

    # Retrieve the existing user from the database
    user = session.query(User).filter(User.id == user_id).first()

    if user:
        setattr(user, "show_sql", st.session_state.show_sql)
        setattr(user, "show_table", st.session_state.show_table)
        setattr(user, "show_plotly_code", st.session_state.show_plotly_code)
        setattr(user, "show_chart", st.session_state.show_chart)
        setattr(user, "show_question_history", st.session_state.show_question_history)
        setattr(user, "show_summary", st.session_state.show_summary)
        setattr(user, "voice_input", st.session_state.voice_input)
        setattr(user, "speak_summary", st.session_state.speak_summary)
        setattr(user, "show_suggested", st.session_state.show_suggested)
        setattr(user, "show_followup", st.session_state.show_followup)
        setattr(user, "llm_fallback", st.session_state.llm_fallback)
        setattr(user, "min_message_id", st.session_state.min_message_id)
        
        # Commit the changes to the database
        session.commit()

        st.toast("User data updated successfully!")
    else:
        st.error("User not found.")

    # Close the session
    session.close()

def get_user(user_id):
    # Create a new database session
    session = SessionLocal()

    # Query to get the user by ID
    user = session.query(User).filter(User.id == user_id).first()

    # Close the session
    session.close()

    return user

def get_recent_messages():
    max_index = st.session_state.min_message_id

    user_id = st.session_state.cookies.get("user_id")

    # Create a new database session
    session = SessionLocal()

    # Query to get the last 20 messages for the user, excluding those with an index greater than max_index
    messages = session.query(Message).filter(
        Message.user_id == user_id,
        Message.id > max_index
    ).order_by(Message.created_at.desc()).limit(20).all()

    # Close the session
    session.close()

    messages.reverse()

    return messages

def delete_all_messages():
    user_id = st.session_state.cookies.get("user_id")

    # Create a new database session
    session = SessionLocal()

    session.query(Message).filter(Message.user_id == user_id).delete()
    session.commit()

    # Close the session
    session.close()

    st.toast("All messages deleted successfully!")

    st.session_state.messages = []