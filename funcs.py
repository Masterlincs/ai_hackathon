import requests
import json

def summarise_blurb(blurb, api_key):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": blurb,
        "parameters": {"max_length": 200, "min_length": 50}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()[0]['summary_text']

def write_new_blurb(blurb_summary, api_key):
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": blurb_summary,
        "parameters": {"max_length": 200, "num_beams": 5}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()[0]['generated_text']

def compare_blurbs(blurb, ai_blurb, api_key):
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": {
            "source_sentence": blurb,
            "sentences": [ai_blurb]
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()