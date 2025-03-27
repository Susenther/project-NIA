import streamlit as st
import ollama
import time
import shelve
import pyttsx3
import speech_recognition as sr

# Load chat memory
def load_memory():
    with shelve.open("chat_memory") as db:
        return db.get("messages", [])

def save_memory():
    with shelve.open("chat_memory") as db:
        db["messages"] = st.session_state.messages

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False  
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = False
if "voice_gender" not in st.session_state:
    st.session_state.voice_gender = "Female"
if "voice_input" not in st.session_state:
    st.session_state.voice_input = False

# UI: Dark Mode Toggle
col1, col2 = st.columns([8, 1])
with col2:
    st.session_state.dark_mode = st.toggle("🌙", st.session_state.dark_mode, help="Toggle Dark Mode")

if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
            body { background-color: #121212; color: white; }
            .stButton>button { background-color: #333; color: white; border-radius: 8px; }
            .stTextInput>div>div>input { background-color: #222; color: white; border-radius: 10px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Header
st.markdown("<h1 style='text-align: center;'>💙 Nia - Your AI Companion</h1>", unsafe_allow_html=True)
st.write("<p style='text-align: center;'>A chatbot that listens, understands, and supports you.</p>", unsafe_allow_html=True)

# Voice Settings
st.divider()
st.subheader("⚙ Chat Settings")

col1, col2, col3 = st.columns(3)
with col1:
    st.session_state.voice_enabled = st.toggle("🔊 Voice Response", st.session_state.voice_enabled)
with col2:
    st.session_state.voice_input = st.toggle("🎙 Voice Input", st.session_state.voice_input)
with col3:
    st.session_state.voice_gender = st.radio("🎤 Voice Gender", ["Female", "Male"], horizontal=True)

st.divider()

# 🔊 *Optimized Voice Response (Faster)*
def speak(text):
    if not st.session_state.voice_enabled:
        return
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        engine.setProperty("rate", 200)  # Faster speech
        engine.setProperty("voice", voices[0].id if st.session_state.voice_gender == "Male" else voices[1].id)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        st.error(f"Voice Error: {e}")

# 🎤 *Optimized Voice Input*
def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=4)  # Reduced timeout
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
st.divider()
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
        role = "*You:* " if msg["role"] == "user" else "*Nia:* "
        st.chat_message(msg["role"]).markdown(f"{role} {msg['text']}")

# 💬 *Input Box*
st.divider()
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    user_input = get_voice_input() if st.session_state.voice_input else st.chat_input("Type a message...")

# 🤖 *Process Input (Reduced Delay)*
if user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    save_memory()

    typing_indicator = st.empty()
    typing_indicator.markdown("Nia is typing...")
    
    # *Reduced Typing Delay*
    time.sleep(1)  # Instant response instead of long delay

    # AI Response
    chat_history = st.session_state.messages[-8:]
    ai_prompt = f"""
    You are Nia, an AI companion who provides emotional support. Your tone is warm and human-like. 
    Recent chat history:
    {chat_history}

    User: {user_input}
    Nia:
    """

    response = ollama.chat(model="mistral:latest", messages=[{"role": "user", "content": ai_prompt}], stream=True)
    bot_reply = "".join(chunk["message"]["content"] for chunk in response)
    
    typing_indicator.empty()

    # *Fast Speech Output*
    speak(bot_reply)

    # *Save & Display AI Response*
    st.session_state.messages.append({"role": "assistant", "text": bot_reply})
    save_memory()
    st.rerun()