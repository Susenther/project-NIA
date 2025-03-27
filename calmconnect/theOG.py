import streamlit as st
import ollama
import logging

# Set page configuration
st.set_page_config(page_title="Emotional Support Agent", page_icon="🧠", layout="wide")

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Model to use
MODEL_NAME = "mistral:latest"

# Function to generate AI responses
def generate_response(user_input):
    """Generate AI response and update conversation history."""
    st.session_state.conversation_history.append({"role": "user", "content": user_input})

    try:
        # Generate AI response
        response = ollama.chat(model=MODEL_NAME, messages=st.session_state.conversation_history)
        ai_response = response['message']['content']
    except Exception as e:
        ai_response = "I'm sorry, but I couldn't process your request. Please try again."
        st.error("An error occurred while generating the response.")
        logging.error(f"Error generating response: {e}")

    st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})
    return ai_response

# Styling for card-like design
st.markdown("""
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #F9F9F9;
        color: #333;
    }
    .stApp {
        padding: 20px;
        max-width: 800px;
        margin: auto;
    }
    .card {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.1);
    }
    .stTitle {
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .stButton {
        background-color: #57A2B9;
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .stButton:hover {
        background-color: #3F7A91;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🧠 Emotional Support Agent")

# Display chat history in card format
for msg in st.session_state['conversation_history']:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)  # Add spacing for scrolling

# User input section in a card
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    user_message = st.text_input("Hey What's up!", key="user_input", placeholder="Type your message...")
    if user_message:
        with st.spinner("Thinking..."):
            ai_response = generate_response(user_message)
            with st.chat_message("assistant"):
                st.write(ai_response)
        
        # No need to clear the session state here; the input field will automatically clear after submission
    st.markdown("</div>", unsafe_allow_html=True)

# Interactive features in card format
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