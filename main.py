import streamlit as st
from streamlit_google_auth import Authenticate
import os
from openai import OpenAI
from dotenv import load_dotenv
import database

authenticator = Authenticate(
    secret_credentials_path='./Key2.json',
    cookie_name='my_cookie_name',
    cookie_key='this_is_secret',
    redirect_uri='http://localhost:8501',
)

authenticator.check_authentification()

# Display the login button if the user is not authenticated
authenticator.login()

if not st.session_state.get('connected'):
    st.stop()

user_email = st.session_state['user_info'].get('email')

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

st.title("OpenAI Chatbot")

database.init_db()

st.title(f"Chat Assistant for {st.session_state['user_info'].get('name')}")


st.session_state.messages = database.load_message(user_email)

# Display the user information and logout button if the user is authenticated
if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    database.save_message(user_email, "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

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

if st.sidebar.button('Logout'):
    authenticator.logout()
    st.rerun()