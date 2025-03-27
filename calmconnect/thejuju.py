import streamlit as st
import ollama
import time
import shelve
import pyttsx3
import speech_recognition as sr
from streamlit_option_menu import option_menu
import base64

# 🎨 Set Background Image
def set_bg(image_path):
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()

    css = f"""
    <style>
    body {{
        background-image: url('data:image/png;base64,{encoded_string}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Call this function with your image file
set_bg("background.png")  # Replace with your actual image file name

# 💾 Load Chat Memory
def load_memory():
    with shelve.open("chat_memory") as db:
        return db.get("messages", [])

def save_memory():
    with shelve.open("chat_memory") as db:
        db["messages"] = st.session_state.messages

# 🌟 Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True  # Default Dark Mode
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = False
if "voice_gender" not in st.session_state:
    st.session_state.voice_gender = "Female"
if "voice_input" not in st.session_state:
    st.session_state.voice_input = False

# 🌈 Custom CSS for Beautiful UI
st.markdown(
    """
    <style>
        .stButton>button { background-color: #6a5acd; color: white; border-radius: 8px; }
        .stTextInput>div>div>input { background-color: #2e2e2e; color: white; border-radius: 8px; }
        .stChatMessage { padding: 10px; margin: 5px 0; border-radius: 12px; width: fit-content; }
        .stChatMessage.user { background-color: #4caf50; color: white; text-align: right; }
        .stChatMessage.assistant { background-color: #333; color: white; }
    </style>
    """,
    unsafe_allow_html=True
)

# 🏠 Sidebar Navigation
selected = option_menu(
    menu_title="Nia - AI Companion",
    options=["Chat", "Settings", "About"],
    icons=["chat-text", "gear", "info-circle"],
    menu_icon="robot",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "5px", "background-color": "#333"},
        "icon": {"color": "white", "font-size": "20px"},
        "nav-link": {"color": "white", "font-size": "18px", "margin": "5px"},
        "nav-link-selected": {"background-color": "#6a5acd"},
    }
)

# 🏷 Header
st.markdown("<h1 style='text-align: center;'>💙 Nia - Your AI Companion</h1>", unsafe_allow_html=True)
st.write("<p style='text-align: center;'>A chatbot that listens, understands, and supports you.</p>", unsafe_allow_html=True)

# ⚙ Settings Panel
if selected == "Settings":
    st.subheader("⚙ Chat Settings")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.voice_enabled = st.toggle("🔊 Voice Response", st.session_state.voice_enabled)
    with col2:
        st.session_state.voice_input = st.toggle("🎙 Voice Input", st.session_state.voice_input)
    with col3:
        st.session_state.voice_gender = st.radio("🎤 Voice Gender", ["Female", "Male"], horizontal=True)

    st.stop()

elif selected == "About":
    st.subheader("ℹ About Nia")
    st.write("Nia is an AI-powered chatbot that provides emotional support and natural conversations.")
    st.stop()

# 🔊 *Voice Response*
def speak(text):
    if not st.session_state.voice_enabled:
        return
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        voice_index = 0 if st.session_state.voice_gender == "Male" else 1
        if len(voices) > voice_index:
            engine.setProperty("voice", voices[voice_index].id)
        engine.setProperty("rate", 200)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        st.error(f"Voice Error: {e}")

# 🎤 *Voice Input*
def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=4)
            text = r.recognize_google(audio)
            st.write(f"🗣 You: {text}")
            return text
        except sr.UnknownValueError:
            st.error("😕 Couldn't understand. Try again.")
        except sr.RequestError:
            st.error("⚠ Voice service unavailable.")
        except sr.WaitTimeoutError:
            st.error("⏳ No speech detected.")
        return None

# 🗑 *Clear Chat*
col1, col2, col3 = st.columns([3, 2, 3])
with col2:
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        save_memory()
        st.rerun()

# 💬 *Chat Display*
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        role = "**You:** " if msg["role"] == "user" else "**Nia:** "
        st.chat_message(msg["role"]).markdown(f"{role} {msg['text']}")

# 💬 *Input Box*
st.divider()
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    user_input = get_voice_input() if st.session_state.voice_input else st.chat_input("Type a message...")

# 🤖 *Process Input*
if user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    save_memory()

    typing_indicator = st.empty()
    typing_indicator.markdown("Nia is typing...")

    # *AI Response*
    time.sleep(1)
    chat_history = st.session_state.messages[-5:]
    ai_prompt = f"""
    You are Nia, an AI companion with a warm, supportive, and human-like tone. 
    Recent chat history:
    {chat_history}

    User: {user_input}
    Nia:
    """

    response = ollama.chat(model="mistral:latest", messages=[{"role": "user", "content": ai_prompt}], stream=True)
    bot_reply = "".join(chunk["message"]["content"] for chunk in response)

    typing_indicator.empty()

    # *Voice Output*
    speak(bot_reply)

    # *Save & Display AI Response*
    st.session_state.messages.append({"role": "assistant", "text": bot_reply})
    save_memory()
    st.rerun()
    
