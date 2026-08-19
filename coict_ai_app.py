import streamlit as st
import ollama

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM CSS (BACKGROUND & STYLING)
# ---------------------------------------------------------
st.set_page_config(
    page_title="CoICT Knowledge AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Dark UI and Smooth Styling
custom_css = """
<style>
/* Main Background Styling */
.stApp {
    background: #ffffff;
    color: #0f172a;
    font-family: 'Inter', sans-serif;
}

/* Sidebar Customization */
[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid rgba(0, 0, 0, 0.08);
}
[data-testid="stSidebar"] * {
    color: #0f172a;
}

/* Header Styling */
.main-header {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0.2rem;
}

.sub-header {
    text-align: center;
    color: #475569;
    font-size: 1rem;
    margin-bottom: 2rem;
}

/* Chat Message Card Customization */
[data-testid="stChatMessage"] {
    background-color: #1e293b;
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 10px;
    color: #ffffff;
}
[data-testid="stChatMessage"] * {
    color: #ffffff;
}

/* Chat Input Styling */
[data-testid="stChatInput"] {
    border-radius: 12px;
    border: 1px solid rgba(139, 92, 246, 0.4);
    background-color: #ffffff;
    color: #0f172a;
}

/* Badge Cards in Sidebar */
.dept-card {
    background: #eef2ff;
    border-left: 3px solid #8b5cf6;
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: #0f172a;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SYSTEM PROMPT SETUP FOR COICT DOMAIN
# ---------------------------------------------------------
COICT_SYSTEM_PROMPT = """
Wewe ni Msaidizi wa Kitalaamu wa Kitivo cha CoICT (College of Information and Communication Technologies).
Kazi yako kuu ni kujibu maswali yanayohusu:
1. Data Science & Big Analytics
2. Computer Science & Software Engineering
3. Computer Networking & Cybersecurity
4. Telecommunication Engineering
5. Information and Communication Technology (ICT) na mifumo yote ya Teknolojia.

Unatakiwa kutoa majibu yenye usahihi wa hali ya juu, muundo mzuri (kutumia bullet points au code blocks ikiwa inahitajika), na kwa lugha inayoeleweka vyema (Kiswahili au Kiingereza kulingana na muulizaji).
"""

MODEL_NAME = "qwen2.5:0.5b"

# Idadi ya messages za hivi karibuni zitakazotumwa kwa model
# (kuzuia context isije ikawa kubwa mno na kupunguza speed/quality)
MAX_HISTORY_MESSAGES = 10

# ---------------------------------------------------------
# 3. SIDEBAR NAVIGATION & INFO
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bot.png", width=70)
    st.title("CoICT AI Portal")
    st.markdown("---")

    st.subheader("📌 Maeneo Yanayoshughulikiwa:")
    departments = [
        "📊 Data Science & Analytics",
        "💻 Computer Science",
        "🌐 Computer Networking",
        "📡 Telecommunications",
        "⚙️ ICT & Smart Systems"
    ]
    for dept in departments:
        st.markdown(f'<div class="dept-card">{dept}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.caption("🤖 **Engine:** Ollama (Qwen2.5:0.5b)")
    st.caption("🔒 **Privacy:** 100% Offline / Local Execution")

    if st.button("🧹 Futa Soga (Clear Chat)", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# 4. CHAT INTERFACE & LOGIC
# ---------------------------------------------------------
st.markdown('<div class="main-header">🎓 CoICT AI Knowledge Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Mfumo wa Akili Bandia kwa ajili ya Idara ya Teknolojia na Mawasiliano</div>', unsafe_allow_html=True)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Existing Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Header
if prompt := st.chat_input("Uliza swali linalohusu Data Science, CS, Networking, Telecom au ICT..."):

    # 1. Add user query to chat history & display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate response using Ollama Local Model
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Chukua messages za hivi karibuni tu (kuzuia context kukua bila kikomo)
        recent_messages = st.session_state.messages[-MAX_HISTORY_MESSAGES:]

        # Prepare payload with System Prompt included
        ollama_messages = [{"role": "system", "content": COICT_SYSTEM_PROMPT}] + [
            {"role": m["role"], "content": m["content"]}
            for m in recent_messages
        ]

        try:
            # Stream response directly from local Ollama instance
            stream = ollama.chat(
                model=MODEL_NAME,
                messages=ollama_messages,
                stream=True,
            )

            for chunk in stream:
                full_response += chunk['message']['content']
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            # Save Assistant response to state
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(
                "❌ Mfumo umeshindwa kuwasiliana na Ollama!\n\n"
                f"Hakikisha Ollama inakimbia na modeli imeshakuzwa: `ollama run {MODEL_NAME}`\n\n"
                f"Details: {e}"
            )
