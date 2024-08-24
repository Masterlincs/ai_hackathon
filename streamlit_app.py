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

# Sidebar for API key input
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your Hugging Face API key:", type="password")
    st.info("Your API key is required to use the Hugging Face models.")

# Main content
if api_key:
    with st.form('research_paper'):
        st.subheader("Enter Paper Details")
        arxiv_id = st.text_input("Enter arXiv ID (e.g., 2308.08155):")
        submit_button = st.form_submit_button("Process Paper")

    if submit_button and arxiv_id:
        with st.spinner("Processing..."):
            try:
                paper = ArxivPaper(arxiv_id)
                paper.fetch_details()

                st.subheader("Paper Details")
                st.write(f"Title: {paper.title}")
                st.write(f"Authors: {', '.join(paper.authors)}")

                # Display original and AI-generated summaries side by side
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Original Blurb")
                    st.write(paper.summary)
                with col2:
                    summary = summarise_blurb(paper.summary, api_key)
                    new_blurb = write_new_blurb(summary, api_key)
                    st.subheader("AI-Generated Blurb")
                    st.write(new_blurb)

                # User input for similarity percentage
                with st.form('similarity_form'):
                    st.subheader("Estimate Similarity")
                    user_similarity = st.slider("How similar are the summaries?", 0, 100, 50)
                    submit_similarity_button = st.form_submit_button("Submit")

                if submit_similarity_button:
                    # Display AI-generated similarity percentage
                    similarity = compare_blurbs(paper.summary, new_blurb, api_key)
                    ai_similarity = round((similarity[0] * 100), 3)
                    st.subheader("AI-Generated Similarity")
                    st.write(f"{ai_similarity}%")

                    # Display comparison between user input and AI-generated similarity
                    st.subheader("Comparison")
                    if user_similarity > ai_similarity:
                        st.write(f"You estimated {user_similarity}% similarity, but the AI generated {ai_similarity}% similarity.")
                    elif user_similarity < ai_similarity:
                        st.write(f"You estimated {user_similarity}% similarity, but the AI generated {ai_similarity}% similarity.")
                    else:
                        st.write(f"You estimated {user_similarity}% similarity, which matches the AI generated {ai_similarity}% similarity.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
else:
    st.warning("Please enter your Hugging Face API key in the sidebar to proceed.")