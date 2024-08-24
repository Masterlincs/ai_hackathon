import streamlit as st
from funcs import ArxivPaper, summarise_blurb, write_new_blurb, compare_blurbs

st.set_page_config(page_title="Research Paper Processing App", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
    }
    .stTextArea > div > div > textarea {
        background-color: #ffffff;
    }
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title('Research Paper Processing App')

# Initialize session state
if 'paper' not in st.session_state:
    st.session_state.paper = None
if 'new_blurb' not in st.session_state:
    st.session_state.new_blurb = None
if 'user_similarity' not in st.session_state:
    st.session_state.user_similarity = None
if 'ai_similarity' not in st.session_state:
    st.session_state.ai_similarity = None
if 'stage' not in st.session_state:
    st.session_state.stage = 'input'

# Sidebar for API key input
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your Hugging Face API key:", type="password")
    st.info("Your API key is required to use the Hugging Face models.")

# Main content
if api_key:
    if st.session_state.stage == 'input':
        with st.form('research_paper'):
            st.subheader("Enter Paper Details")
            arxiv_id = st.text_input("Enter arXiv ID (e.g., 2308.08155):")
            submit_button = st.form_submit_button("Process Paper")

        if submit_button and arxiv_id:
            with st.spinner("Processing..."):
                try:
                    paper = ArxivPaper(arxiv_id)
                    paper.fetch_details()
                    summary = summarise_blurb(paper.summary, api_key)
                    new_blurb = write_new_blurb(summary, api_key)
                    
                    st.session_state.paper = paper
                    st.session_state.new_blurb = new_blurb
                    st.session_state.stage = 'display'
                    st.rerun()
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    elif st.session_state.stage == 'display':
        st.subheader("Paper Details")
        st.write(f"Title: {st.session_state.paper.title}")
        st.write(f"Authors: {', '.join(st.session_state.paper.authors)}")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Blurb")
            st.write(st.session_state.paper.summary)
        with col2:
            st.subheader("AI-Generated Blurb")
            st.write(st.session_state.new_blurb)

        with st.form('similarity_form'):
            st.subheader("Estimate Similarity")
            user_similarity = st.slider("How similar are the summaries?", 0, 100, 50)
            submit_similarity_button = st.form_submit_button("Submit")

        if submit_similarity_button:
            st.session_state.user_similarity = user_similarity
            similarity = compare_blurbs(st.session_state.paper.summary, st.session_state.new_blurb, api_key)
            st.session_state.ai_similarity = round((similarity[0] * 100), 3)
            st.session_state.stage = 'results'
            st.rerun()

    elif st.session_state.stage == 'results':
        st.subheader("Paper Details")
        st.write(f"Title: {st.session_state.paper.title}")
        st.write(f"Authors: {', '.join(st.session_state.paper.authors)}")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Blurb")
            st.write(st.session_state.paper.summary)
        with col2:
            st.subheader("AI-Generated Blurb")
            st.write(st.session_state.new_blurb)

        st.subheader("Similarity Comparison")
        st.write(f"Your estimated similarity: {st.session_state.user_similarity}%")
        st.write(f"AI-generated similarity: {st.session_state.ai_similarity}%")

        if st.session_state.user_similarity > st.session_state.ai_similarity:
            st.write(f"You estimated a higher similarity than the AI.")
        elif st.session_state.user_similarity < st.session_state.ai_similarity:
            st.write(f"You estimated a lower similarity than the AI.")
        else:
            st.write(f"Your estimation matches the AI-generated similarity.")

        if st.button("Process Another Paper"):
            st.session_state.stage = 'input'
            st.rerun()

else:
    st.warning("Please enter your Hugging Face API key in the sidebar to proceed.")