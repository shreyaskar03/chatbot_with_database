import os
import streamlit as st
import requests
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("API Key not found. Please set GEMINI_API_KEY using setx.")
    st.stop()

# Updated Gemini API URL with the correct model and API version
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-001:generateContent?key={GEMINI_API_KEY}"

def get_gemini_response(prompt):
    """Function to send a request to Gemini API and return response."""
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        response_json = response.json()
        return response_json["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Streamlit UI
st.title("Message History Chat App")

# User input
user = st.text_input("Enter your username")
qsn = st.text_input("Enter your question")

if user and qsn:
    try:
        # MongoDB chat history setup
        chat_with_history = MongoDBChatMessageHistory(
            session_id=user,
            connection_string="mongodb+srv://Shreyaskar:llm1234@cluster0.7m1rn.mongodb.net",
            database_name="langchain",
            collection_name="chat_history"
        )

        # Add user message to history
        chat_with_history.add_user_message(qsn)

        # Get Gemini response
        response_text = get_gemini_response(qsn)

        if response_text:
            # Add AI response to history
            chat_with_history.add_ai_message(response_text)

            # Display response
            st.write("AI Response:", response_text)

            # Display chat history in a user-friendly format
            st.subheader("Chat History")
            for message in chat_with_history.messages:
                with st.chat_message(name=message.type):  # "human" or "ai"
                    st.write(message.content)
        else:
            st.error("Failed to get a response from Gemini API.")

    except Exception as e:
        st.error(f"An error occurred: {e}")