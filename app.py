import streamlit as st
from streamlit_lottie import st_lottie
import requests
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from gtts import gTTS 
import os
from streamlit_mic_recorder import mic_recorder, speech_to_text
from dotenv import load_dotenv
import time

# --- 1. SETTINGS & KEY ---
# Sami bhai, maine key yahan direct daal di hai taake aapka foran chal jaye
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# --- 2. FUNCTIONS ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Animation load karna
lottie_waves = load_lottieurl("https://lottie.host/85906560-f103-4903-8d00-47963f25c7e3/Z8R6I9YQv4.json")

# --- 3. PAGE SETUP ---
st.set_page_config(page_title="AI-Agent صراط مستقیم", page_icon="🌙")
st.title("🌙 AI-Agent صراط مستقیم")
st.write("The great adviser to earn in halal way - Islamic path for students")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 4. AI MODEL SETUP ---
system_msg = (
    "You are an Islamic teacher and guide students to earn halal income. "
    "Always say: 'Never go to the path of haram'. "
    "If someone asks about trading and crypto, explain why they are haram. "
    "Reply in the language the user uses. Be motivational!"
    "never say sawagat hai or namashkar, just give advice in a friendly way. Always end with a motivational note."
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an Islamic guider. Remember context: " + system_msg),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Model ko key dena
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.9, api_key=openai_api_key)
chain = prompt_template | llm

# --- 5. VOICE INPUT SECTION ---
st.subheader("Talk to your Mentor")
text_from_voice = speech_to_text(
    start_prompt="🎤 Click to Speak",
    stop_prompt="🛑 Stop Recording",
    language="en",
    use_container_width=True,
    key='my_stt_button'
)

# --- 6. MAIN CHAT INTERFACE ---
# Voice se aaya hua text ya type kiya hua text
user_input = st.text_input("Ask question from agent:", value=text_from_voice if text_from_voice else "")

if st.button("Get Advice"):
    if user_input:
        # LOGIC: Jab AI sochega tab Lottie Waves aur Spinner nazar aayengi
        with st.spinner("Mursal is thinking..."):
            # Pehle waves dikhao
            if lottie_waves:
                st_lottie(lottie_waves, height=150, key="processing_waves")
            
            # AI Response
            try:
                response = chain.invoke({
                    "input": user_input,
                    "history": st.session_state.chat_history
                })
                
                # Context Update
                st.session_state.chat_history.append(HumanMessage(content=user_input))
                st.session_state.chat_history.append(AIMessage(content=response.content))
                
                # Result Display
                st.success(response.content)

                # --- VOICE OUTPUT ---
                tts = gTTS(text=response.content, lang='ur')
                audio_file = f"response_{int(time.time())}.mp3"
                tts.save(audio_file)
                st.audio(audio_file, format="audio/mp3", autoplay=True)
                
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Pehle kuch likhein ya mic use karein!")

# --- 7. CLEAR OPTION ---
st.divider()
if st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()
