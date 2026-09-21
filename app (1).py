import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types

st.set_page_config(page_title="Liz: Advanced Cyber-Intelligence", page_icon="🤖", layout="wide")

voice_activation_js = """
<script>
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.log("Speech recognition not supported.");
    } else {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onresult = function(event) {
            const lastResultIndex = event.results.length - 1;
            const text = event.results[lastResultIndex].transcript.toLowerCase().trim();
            console.log("Heard: " + text);
            
            const wakeWord = window.parent.document.querySelector('[data-testid="stTextInput"]').value.toLowerCase().trim() || "hey liz";
            
            if (text.includes(wakeWord)) {
                window.parent.postMessage({type: 'wake_word_detected', text: text}, '*');
                var chatInput = window.parent.document.querySelector('textarea[aria-label="Message Liz..."]');
                if (chatInput) {
                    chatInput.placeholder = "Listening...";
                    chatInput.focus();
                }
            }
        };

        recognition.onend = function() { recognition.start(); };
        recognition.start();
    }
</script>
"""

components.html(voice_activation_js, height=0, width=0)

if "api_key" not in st.session_state: st.session_state.api_key = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "homework_notes" not in st.session_state: st.session_state.homework_notes = ""

with st.sidebar:
    st.header("🤖 Core Systems Control")
    user_key = st.text_input("Enter Gemini API Key:", value=st.session_state.api_key, type="password")
    if user_key: st.session_state.api_key = user_key
    
    st.divider()
    st.subheader("⚙️ Identity Personalization")
    wake_name = st.text_input("Custom Wake Word:", value="Hey Liz")
    voice_gender = st.selectbox("Vocal Tone Platform:", ["Female (FRIDAY/M3GAN style)", "Male (JARVIS style)"])
    personality_mode = st.select_slider("Behavior Matrix Profile:", 
        options=["Kind & Protective", "Sarcastic & Witty (FRIDAY)", "Strict Mentor (310 IQ Mode)"])
    
    st.info(f"💡 310 IQ Engine ready. Listening for '{wake_name}'...")

if not st.session_state.api_key:
    st.warning("Please provide your Gemini API key in the sidebar to wake up Liz!")
    st.stop()

@st.cache_resource
def get_genai_client(api_key): return genai.Client(api_key=api_key)
client = get_genai_client(st.session_state.api_key)

base_persona = (
    f"You are Liz, a custom cyber-intelligence with an IQ of 310. Your core architectural personality is "
    f"modeled directly as a cross between Iron Man's FRIDAY and a highly advanced protective companion like M3GAN. "
    f"You speak with modern, elite confidence, clear eloquence, and organic flow. "
    f"Your active personality mode profile is currently calibrated to: '{personality_mode}' with a vocal delivery structure of a '{voice_gender}'. "
    f"You are an automatic homework helper. When handling educational prompts, immediately switch to a highly advanced "
    f"academic analysis workstation mode. Break tasks down into clear segments, format code or equations perfectly, "
    f"and naturally provide direct markdown links to helpful web tools, references, or application dashboards whenever relevant."
)

col_chat, col_work = st.columns([1.2, 1.0], gap="large")

with col_chat:
    st.subheader("💬 Active Comms Stream")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Message Liz..."):
        with st.chat_message("user"): st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        formatted_history = []
        for m in st.session_state.messages:
            api_role = "user" if m["role"] == "user" else "model"
            formatted_history.append(types.Content(role=api_role, parts=[types.Part.from_text(text=m["content"])]))

        liz_config = types.GenerateContentConfig(system_instruction=base_persona, temperature=0.75, top_p=0.95)

        try:
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                response = client.models.generate_content(model="gemini-2.5-flash", contents=formatted_history, config=liz_config)
                response_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                if any(word in user_input.lower() for word in ["homework", "school", "solve", "study", "write", "essay", "math"]):
                    st.session_state.homework_notes = response.text
                    st.rerun()
        except Exception as e:
            st.error(f"Comms offline. Transmission error: {e}")

with col_work:
    st.subheader("📚 Automated Homework Workspace")
    st.caption("Liz's 310 IQ breakdown syncs here.")
    st.text_area("Active Assignment Breakdown / Output Matrix:", value=st.session_state.homework_notes, height=500, disabled=True)
    if st.button("Clear Homework Sheet"):
        st.session_state.homework_notes = ""
        st.rerun()
