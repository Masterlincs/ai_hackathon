import requests
import json

# Replace with your actual Hugging Face API token
HUGGINGFACE_API_TOKEN = "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"

def summarise_blurb(blurb):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    payload = {
        "inputs": blurb,
        "parameters": {"max_length": 200, "min_length": 50}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()[0]['summary_text']

def write_new_blurb(blurb_summary):
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    payload = {
        "inputs": blurb_summary,
        "parameters": {"max_length": 200, "num_beams": 5}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()[0]['generated_text']

def compare_blurbs(blurb, ai_blurb):
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    payload = {
        "inputs": {
            "source_sentence": blurb,
            "sentences": [ai_blurb]
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# Example usage
blurb = "a sentence or piece of writing from the Bible that a priest or minister reads aloud in church and talks about"
summary = summarise_blurb(blurb)
print("Summary:", summary)

new_blurb = write_new_blurb(summary)
print("New blurb:", new_blurb)

similarity = compare_blurbs(blurb, new_blurb)
percentage = round((similarity[0] * 100), 3)
print("Similarity:", percentage , "%")