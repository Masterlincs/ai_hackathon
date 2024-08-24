import streamlit as st
from funcs import summarise_blurb, write_new_blurb, compare_blurbs


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
        blurb = st.text_area("Paste your arXiv link or paper blurb here:", height=150)
        submit_button = st.form_submit_button("Process Paper")

    if submit_button and blurb:
        with st.spinner("Processing..."):
            try:
                summary = summarise_blurb(blurb, api_key)
                st.subheader("Summary")
                st.write(summary)

                new_blurb = write_new_blurb(summary, api_key)
                st.subheader("New Blurb")
                st.write(new_blurb)

                similarity = compare_blurbs(blurb, new_blurb, api_key)
                percentage = round((similarity[0] * 100), 3)
                st.subheader("Similarity")
                st.write(f"{percentage}%")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
else:
    st.warning("Please enter your Hugging Face API key in the sidebar to proceed.")