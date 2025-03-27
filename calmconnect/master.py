import streamlit as st
import ollama
import time
import shelve
import os
import pygame  # For playing audio
from elevenlabs import set_api_key, Voice, VoiceSettings, generate

# Initialize pygame mixer
pygame.mixer.init()

# Set ElevenLabs API Key
set_api_key("YOUR_ELEVENLABS_API_KEY")  # Replace with your actual API key

# Load or initialize chat memory
def load_memory():
    try:
        with shelve.open("chat_memory") as db:
            return db.get("messages", [])
    except Exception as e:
        st.error(f"Error loading chat memory: {e}")
        return []

def save_memory():
    try:
        with shelve.open("chat_memory") as db:
            db["messages"] = st.session_state.messages
    except Exception as e:
        st.error(f"Error saving chat memory: {e}")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = load_memory()
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = False  # Default: Voice OFF
if 'voice_gender' not in st.session_state:
    st.session_state.voice_gender = "Female"  # Default voice

# Streamlit app configuration
st.set_page_config(page_title="Your AI Companion", layout="centered")
st.title("Chat with Me")
st.write("Your AI companion who truly cares.")

# Custom CSS for chat messages
st.markdown("""
    <style>
    .user-message {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 70%;
        margin-left: auto;
    }
    .nia-message {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 70%;
        margin-right: auto;
    }
    .typing {
        color: #888;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

# Toggle voice option
st.session_state.voice_enabled = st.checkbox("🔊 Enable Voice Response", st.session_state.voice_enabled)

# Dropdown for voice selection
st.session_state.voice_gender = st.selectbox("🎤 Choose Voice Gender", ["Female", "Male"], index=0)

# Function to speak text using ElevenLabs
def speak(text):
    if not st.session_state.voice_enabled:
        return
    try:
        # Select voice based on gender
        voice_id = "EXAVITQu4vr4xnSDxMaL"  # Bella's voice ID (Female)
        if st.session_state.voice_gender == "Male":
            voice_id = "TxGEqnHWrfWFTfGW9XjX"  # Josh's voice ID (Male)

        # Generate speech with ElevenLabs
        audio = generate(
            text=text,
            voice=Voice(voice_id=voice_id, settings=VoiceSettings(stability=0.5, similarity_boost=0.8))
        )

        # Save the audio to a temporary file
        with open("temp_audio.mp3", "wb") as f:
            f.write(audio)

        # Play the generated audio
        pygame.mixer.music.load("temp_audio.mp3")
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        # Clean up the temporary file
        os.remove("temp_audio.mp3")
    except Exception as e:
        st.error(f"Voice Error: {e}")

# Display chat history
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        role_class = "user-message" if msg['role'] == 'user' else "nia-message"
        st.markdown(f"<div class='{role_class}'>{msg['text']}</div>", unsafe_allow_html=True)

# Clear chat button
if st.button("🗑 Clear Chat History"):
    st.session_state.messages = []
    save_memory()
    st.experimental_rerun()

# User input
user_input = st.chat_input("Type a message...")
if user_input:
    st.session_state.messages.append({'role': 'user', 'text': user_input})
    save_memory()

    # Show typing effect
    typing_indicator = st.empty()
    typing_indicator.markdown("<div class='typing'>Nia is typing...</div>", unsafe_allow_html=True)
    
    # Simulate human-like typing delay
    time.sleep(min(3, max(1.5, len(user_input) * 0.05)))

    # Keep only last 8 messages to maintain relevant chat memory
    chat_history = st.session_state.messages[-8:]

    # Generate AI response with memory
    ai_prompt = f"""
    You are Nia, an AI companion who provides emotional support. Your tone should be warm, casual, and human-like. Keep responses short but meaningful. 
    Here is the recent chat history:
    {chat_history}
    
    User: {user_input}
    Nia:"""

    response = ollama.chat(model='mistral:latest', messages=[{"role": "user", "content": ai_prompt}], stream=True)

    bot_reply = ""
    for chunk in response:
        bot_reply += chunk['message']['content']
        # Update the UI with the partial response
        typing_indicator.markdown(f"<div class='nia-message'>{bot_reply}</div>", unsafe_allow_html=True)
        time.sleep(0.05)  # Simulate typing delay

    bot_reply = bot_reply.strip()

    typing_indicator.empty()

    # Speak if voice is enabled
    speak(bot_reply)

    # Save and display AI response
    st.session_state.messages.append({'role': 'assistant', 'text': bot_reply})
    save_memory()
    st.experimental_rerun() 