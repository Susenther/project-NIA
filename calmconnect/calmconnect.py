import streamlit as st
import ollama
import logging

# Set page configuration
st.set_page_config(page_title="Emotional Support Agent", page_icon="🧠", layout="wide")

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False  # Flag to check if we are processing input

# Model to use
MODEL_NAME = "mistral:latest"

# Function to generate AI responses
def generate_response(user_input):
    """Generate AI response and update conversation history."""
    st.session_state.conversation_history.append({"role": "user", "content": user_input})

    try:
        response = ollama.chat(model=MODEL_NAME, messages=st.session_state.conversation_history)
        ai_response = response['message']['content']
    except Exception as e:
        ai_response = "I'm sorry, but I couldn't process your request. Please try again."
        st.error("An error occurred while generating the response.")
        logging.error(f"Error generating response: {e}")

    st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})
    return ai_response

# Styling for a clean, blue input field design
st.markdown("""
    <style>
    body {
        font-family: 'Roboto', sans-serif;
        background: linear-gradient(135deg, #1e2a47, #667eea);
        color: #fff;
        margin: 0;
        overflow-x: hidden;
    }
    .stApp {
        padding: 30px;
        max-width: 900px;
        margin: auto;
    }
    .card {
        background-color: rgba(0, 0, 0, 0.5);
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 30px;
        box-shadow: 0px 12px 20px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(8px);
    }
    .stTitle {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 25px;
        color: #f8f9fa;
        text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.4);
    }
    .chat-message {
        background-color: #ffffff;
        color: #333;
        padding: 15px;
        border-radius: 18px;
        margin-bottom: 20px;
        font-size: 16px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        width: max-content;
        max-width: 70%;
        transition: transform 0.3s;
    }
    .user-message {
        background-color: #667eea;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    .assistant-message {
        background-color: #f1f3f5;
        color: #333;
        margin-right: auto;
        text-align: left;
    }
    .chat-message:hover {
        transform: scale(1.05);
    }
    .input-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 20px;
    }
    .input-box input {
        width: 85%;
        padding: 15px;
        font-size: 18px;
        border-radius: 30px;
        border: 2px solid #667eea;
        background-color: rgba(255, 255, 255, 0.8);
        color: #333;
        box-shadow: 0px 6px 14px rgba(0, 0, 0, 0.1);
        transition: border 0.3s;
    }
    .input-box input:focus {
        outline: none;
        border: 2px solid #4f8df1;  /* Blue color when focused */
    }
    .input-box button {
        background-color: #667eea;
        color: white;
        padding: 15px 20px;
        border-radius: 30px;
        border: none;
        cursor: pointer;
        font-weight: bold;
        transition: background-color 0.3s, transform 0.3s;
    }
    .input-box button:hover {
        background-color: #5560ea;
        transform: scale(1.05);
    }
    .input-box button:active {
        background-color: #4d54e7;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🧠 AI Emotional Support")

# Display chat history with sleek modern design
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='chat-message-box'>", unsafe_allow_html=True)
    for msg in st.session_state['conversation_history']:
        with st.chat_message(msg["role"]):
            message_class = "user-message" if msg["role"] == "user" else "assistant-message"
            st.markdown(f"<div class='{message_class}'>{msg['content']}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

# User input section with modern design
with st.form("chat_form"):
    st.markdown("<div class='input-box'>", unsafe_allow_html=True)
    user_message = st.text_input("", placeholder="Type your message...", key="input_box", label_visibility="collapsed")
    submit_button = st.form_submit_button("Send")

    st.markdown("</div>", unsafe_allow_html=True)

if submit_button and user_message:
    # Prevent repeated responses
    if not st.session_state.is_processing:
        st.session_state.is_processing = True  # Set processing flag to True

        # Generate AI response
        ai_response = generate_response(user_message)

        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(f"<div class='assistant-message'>{ai_response}</div>", unsafe_allow_html=True)

        # Reset processing flag after response
        st.session_state.is_processing = False  # Reset processing flag after response

        # Optional: Use rerun to refresh the UI after input reset
        st.rerun()  # Trigger a page rerun to clear the input field

# Interactive Features: Affirmation and Meditation
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    with st.expander("💬 Need Encouragement?"):
        if st.button("Give me a Positive Affirmation"):
            affirmation = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": "Give me a positive affirmation."}])
            st.markdown(f"**AI**: {affirmation['message']['content']}")
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    with st.expander("🧘 Try a Relaxing Meditation:"):
        if st.button("Give me a Guided Meditation"):
            meditation = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": "Give me a guided meditation."}])
            st.markdown(f"**AI**: {meditation['message']['content']}")
    st.markdown("</div>", unsafe_allow_html=True)
