import streamlit as st
from streamlit_google_auth import Authenticate
import os
from openai import OpenAI
from dotenv import load_dotenv
import database
from datetime import datetime


def validate_session():
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = datetime.now()
    elif (datetime.now() - st.session_state.last_activity).seconds > 3600:
        authenticator.logout()
        st.error("Session expired. Please log in again.")
        st.rerun()

authenticator = Authenticate(
    secret_credentials_path='./Key2.json',
    cookie_name='my_cookie_name',
    cookie_key='this_is_secret',
    redirect_uri='http://localhost:8501',
)

authenticator.check_authentification()


# Display the login button if the user is not authenticated
if not st.session_state.get('connected'):
    st.header("Welcome to OpenAI Chatbot")
    st.header("Please sign in with your google account to continue")
    authenticator.login()
    validate_session()
    st.stop()
else:
    user_email = st.session_state['user_info'].get('email')

    load_dotenv()

    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key or not openai_api_key.startswith('sk-'):
        st.error("Invalid OpenAI API key configuration")
        st.stop()

    try:
        client = OpenAI(api_key=openai_api_key)
        # Test API connection
        client.models.list()
    except Exception as e:
        st.error(f"OpenAI connection failed: {str(e)}")
        st.stop()

    st.title("OpenAI Chatbot")

    database.init_db()

    st.title(f"Chat Assistant for {st.session_state['user_info'].get('name')}")

    try:
        loaded_messages = database.load_message(user_email)
        if not isinstance(loaded_messages, list):
            raise ValueError("Invalid message format")

        st.session_state.messages = [
            msg for msg in loaded_messages
            if isinstance(msg, dict) and "role" in msg and "content" in msg
        ]
    except Exception as e:
        st.error("Failed to load chat history")
        st.session_state.messages = []

    # Display the user information and logout button if the user is authenticated
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What's on your mind?"):
        clean_prompt = prompt.strip()

        if len(clean_prompt) == 0:
            st.error("Please enter a valid message")
        elif len(clean_prompt) > 1000:
            st.error("Message exceeds 1000 character limit")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            database.save_message(user_email, "user", prompt)

            with st.chat_message("user"):
                st.markdown(prompt)

            try:
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    for response in client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                            stream=True,
                    ):
                        full_response += (response.choices[0].delta.content or "")
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)

                st.session_state.messages.append({"role": "assistant", "content": full_response})
                database.save_message(user_email, "assistant", full_response)
            except Exception as e:
                error_msg = f"API Error: {str(e)}"
                st.error(error_msg)

    if st.sidebar.button('Logout'):
        authenticator.logout()
        st.rerun()