import streamlit as st
import random
from funcs import ArxivPaper, summarise_blurb, write_new_blurb, compare_blurbs, is_valid_api_key, fetch_random_valid_paper_details

st.set_page_config(page_title="Research Paper Processing App", layout="wide")

# Custom CSS for light and dark mode
st.markdown("""
    <style>
    /* Light mode styles */
    @media (prefers-color-scheme: light) {
        .title {
            color: #000000;
        }
        .warning {
            color: #FF0000;
        }
        .main {
        padding: 2rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        }
    }

    /* Dark mode styles */
    @media (prefers-color-scheme: dark) {
        .title {
            color: #ffffff;
        }
        .warning {
            color: #FFA07A;
        }
        .main {
        padding: 2rem;
        border-radius: 0.5rem;
        background-color: #050505;
        }
    }

    /* Styles for input fields and buttons */
    .stTextInput > div > div > input {
        background-color: var(--background-secondary);
        color: var(--text-color);
    }
    .stTextArea > div > div > textarea {
        background-color: var(--background-secondary);
        color: var(--text-color);
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

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
if 'summaries' not in st.session_state:
    st.session_state.summaries = []
if 'correct_index' not in st.session_state:
    st.session_state.correct_index = None

# Sidebar for API key input and page selection
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your Hugging Face API key:", type="password")
    
    if st.button("Validate API Key"):
        if is_valid_api_key(api_key):
            st.success("API key is valid!")
            st.session_state.api_key = api_key
        else:
            st.error("Invalid API key. Please try again.")
    
    st.header("Navigation")
    page = st.radio("Select Page", ["arXiv Input", "Random arXiv", "Sandbox"])

# Main content
if 'api_key' in st.session_state:
    if page == "arXiv Input":
        st.markdown('<h1 class="title">arXiv Paper Processing</h1>', unsafe_allow_html=True)
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
                        summary = summarise_blurb(paper.summary, st.session_state.api_key)
                        new_blurb = write_new_blurb(summary, st.session_state.api_key)
                        
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
                similarity = compare_blurbs(st.session_state.paper.summary, st.session_state.new_blurb, st.session_state.api_key)
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

    elif page == "Random arXiv":
        st.markdown('<h1 class="title">Random arXiv Guessing Game</h1>', unsafe_allow_html=True)
        
        if st.session_state.stage == 'input':
            if st.button("Get Random arXiv Paper"):
                with st.spinner("Fetching and processing random arXiv paper..."):
                    random_arxiv_id = fetch_random_valid_paper_details()
                    if random_arxiv_id:
                        paper = ArxivPaper(random_arxiv_id)
                        if paper.fetch_details():
                            ai_summary = summarise_blurb(paper.summary, st.session_state.api_key)
                            
                            st.session_state.paper = paper
                            st.session_state.summaries = [paper.summary, ai_summary]
                            random.shuffle(st.session_state.summaries)
                            st.session_state.correct_index = st.session_state.summaries.index(paper.summary)
                            st.session_state.stage = 'guess'
                            st.rerun()
                        else:
                            st.error("Failed to fetch paper details. Please try again.")
                    else:
                        st.error("Failed to find a valid random arXiv paper. Please try again.")

        elif st.session_state.stage == 'guess':
            st.subheader("Random Paper Details")
            st.write(f"Title: {st.session_state.paper.title}")
            st.write(f"Authors: {', '.join(st.session_state.paper.authors)}")

            st.subheader("Guess the Original Summary")
            st.write("Below are two summaries. One is the original arXiv summary, and the other is AI-generated. Can you guess which one is the original?")

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Summary A")
                st.write(st.session_state.summaries[0])
            with col2:
                st.subheader("Summary B")
                st.write(st.session_state.summaries[1])

            user_guess = st.radio("Which summary do you think is the original?", ["Summary A", "Summary B"])
            
            if st.button("Submit Guess"):
                user_guess_index = 0 if user_guess == "Summary A" else 1
                if user_guess_index == st.session_state.correct_index:
                    st.success("Correct! You guessed the original summary.")
                else:
                    st.error("Incorrect. The other summary was the original.")
                
                st.subheader("Original Summary")
                st.write(st.session_state.paper.summary)
                
                st.subheader("AI-Generated Summary")
                st.write(st.session_state.summaries[1 - st.session_state.correct_index])
                
                if st.button("Play Again"):
                    st.session_state.stage = 'input'
                    st.session_state.paper = None
                    st.session_state.summaries = []
                    st.session_state.correct_index = None
                    st.rerun()

    elif page == "Sandbox":
        st.markdown('<h1 class="title">Text Input</h1>', unsafe_allow_html=True)
        
        if st.session_state.stage == 'input':
            with st.form('text_input'):
                st.subheader("Enter Text")
                text_input = st.text_area("Enter any text:", height=200)
                submit_button = st.form_submit_button("Process Text")

            if submit_button and text_input:
                with st.spinner("Processing..."):
                    try:
                        summary = summarise_blurb(text_input, st.session_state.api_key)
                        new_blurb = write_new_blurb(summary, st.session_state.api_key)
                        
                        st.session_state.text_input = text_input
                        st.session_state.new_blurb = new_blurb
                        st.session_state.stage = 'display'
                        st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

        elif st.session_state.stage == 'display':
            st.subheader("Text Details")
            st.write("Original Text:")
            st.write(st.session_state.text_input)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original Blurb")
                st.write(st.session_state.text_input)
            with col2:
                st.subheader("AI-Generated Blurb")
                st.write(st.session_state.new_blurb)

            st.subheader("AI-Generated Similarity")
            similarity = compare_blurbs(st.session_state.text_input, st.session_state.new_blurb, st.session_state.api_key)
            st.write(f"AI-generated similarity: {round((similarity[0] * 100), 3)}%")

            if st.button("Process Another Text"):
                st.session_state.stage = 'input'
                st.rerun()

else:
    st.warning("Please enter your Hugging Face API key in the sidebar to proceed.")