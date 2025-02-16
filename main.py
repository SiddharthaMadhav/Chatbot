import streamlit as st
from auth import AuthManager
from llm_handler import LLMClient
from session_manager import SessionManager
from database import DatabaseManager


auth_manager = AuthManager()
db_manager = DatabaseManager()
llm_client = LLMClient()

# Authentication flow
user_info = auth_manager.check_auth()
session_manager = SessionManager(auth_manager)
session_manager.validate_session()

# Initialize chat
db_manager.init_db()
st.title(f"Chat Assistant for {user_info.get('name')}")

# Load message history
if 'messages' not in st.session_state:
    st.session_state.messages = db_manager.load_message(user_info['email'])

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def handle_user_input(prompt, email, db_manager, llm_client):
    clean_prompt = prompt.strip()
    if not clean_prompt:
        st.error("Please enter a valid message")
        return
    if len(clean_prompt) > 1000:
        st.error("Message exceeds 1000 character limit")
        return

    try:
        # Save user message
        st.session_state.messages.append({"role": "user", "content": clean_prompt})
        db_manager.save_message(email, "user", clean_prompt)

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            for response in llm_client.generate_response(
                    [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            ):
                chunk = response.choices[0].delta.content or ""
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        db_manager.save_message(email, "assistant", full_response)

    except Exception as e:
        st.error(f"Error processing request: {str(e)}")

# Chat input handling
if prompt := st.chat_input("What's on your mind?"):
    handle_user_input(prompt, user_info['email'], db_manager, llm_client)

# Sidebar controls
if st.sidebar.button('Logout'):
    auth_manager.logout()