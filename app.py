#  app.py
import streamlit as st
from main import run_pipeline
from core.rag_engine import ask_question

# 1. Page Config (Must be the first Streamlit command)
st.set_page_config(page_title="MeetingMind AI", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# 2. Custom CSS for extra polish
st.markdown("""
    <style>
    /* Soften the background of the main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Style the tabs to look more like buttons */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        background-color: #f0f2f6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b;
        color: gold !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm ready to answer questions about your video."}]

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4230/4230551.png", width=80) # Placeholder logo
    st.title("Settings & Input")
    st.markdown("Enter a video source to generate insights and enable RAG chat.")
    
    uploaded = st.file_uploader(
    "Upload audio/video",
    type=["mp3", "wav", "mp4", "m4a"]
    )

    source = uploaded

    language = st.selectbox(
    "🌐 Spoken Language",
    ["english", "hinglish"],
    index=0
     )
    
    st.divider()
    process_button = st.button("✨ Process Video", type="primary", use_container_width=True)
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm ready to answer questions about your video."}]
        st.rerun()

    st.markdown("---")
    st.caption("Powered by LLMs & Streamlit")

# --- MAIN APP HEADER ---
st.title("🧠 MeetingMind AI — Video Intelligence Platform")
st.markdown("Turn long meetings and videos into searchable, actionable insights with RAG-powered analysis.")

# --- PROCESSING LOGIC ---
if process_button and source:
    with st.status("🧠 AI is analyzing your video...", expanded=True) as status:
        try:
            st.write("Extracting audio and transcribing...")
            result = run_pipeline(source, language)
            st.session_state.processed_data = result
            st.session_state.messages = [{"role": "assistant", "content": f"I've finished analyzing '{result['title']}'. What would you like to know?"}]
            
            status.update(label="Analysis Complete!", state="complete", expanded=False)
            st.balloons() # Fun animation on success
        except Exception as e:
            status.update(label="Error during processing", state="error")
            st.error(f"An error occurred: {e}")

# --- DASHBOARD UI ---
if st.session_state.processed_data:
    data = st.session_state.processed_data

    st.header(f"📌 {data['title']}")
    
    # Use Metrics for a quick "at-a-glance" look (Mocking counts for visual effect)
    m1, m2, m3 = st.columns(3)
    m1.metric(label="Status", value="Processed ✅")
    m2.metric(label="Action Items Found", value=len(data['action_items'].split('\n')) if data['action_items'] else 0)
    m3.metric(label="Open Questions", value=len(data['open_questions'].split('\n')) if data['open_questions'] else 0)
    
    st.divider()

    # Use Tabs to organize information cleanly instead of long scrolling pages
    tab1, tab2, tab3 = st.tabs(["📝 Summary", "🎯 Insights & Actions", "💬 Interactive Chat"])

    with tab1:
        st.subheader("Executive Summary")
        st.info(data['summary'], icon="📄")

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ Action Items")
            st.success(data['action_items'])
        with col2:
            st.subheader("🔑 Key Decisions")
            st.warning(data['key_decisions'])
            
        st.subheader("❓ Open Questions")
        st.error(data['open_questions'])

    with tab3:
        st.subheader("Chat with the Video Context")
        
        # Display chat history with custom avatars
        for message in st.session_state.messages:
            avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask a question about the meeting..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Searching transcripts..."):
                    rag_chain = data["rag_chain"]
                    answer = ask_question(rag_chain, prompt)
                    st.markdown(answer)
            
            st.session_state.messages.append({"role": "assistant", "content": answer})