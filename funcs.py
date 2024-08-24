import requests
import xml.etree.ElementTree as ET

class ArxivPaper:
    def __init__(self, arxiv_id):
        self.arxiv_id = arxiv_id
        self.title = None
        self.authors = []
        self.summary = None

    def fetch_details(self):
        base_url = "http://export.arxiv.org/api/query"
        params = {"id_list": self.arxiv_id}
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            entry = root.find('{http://www.w3.org/2005/Atom}entry')
            
            if entry is not None:
                title_element = entry.find('{http://www.w3.org/2005/Atom}title')
                if title_element is not None:
                    self.title = title_element.text.strip()
                
                summary_element = entry.find('{http://www.w3.org/2005/Atom}summary')
                if summary_element is not None:
                    self.summary = summary_element.text.strip()
                
                author_elements = entry.findall('{http://www.w3.org/2005/Atom}author')
                for author_element in author_elements:
                    name_element = author_element.find('{http://www.w3.org/2005/Atom}name')
                    if name_element is not None:
                        self.authors.append(name_element.text.strip())
            else:
                print("No entry found for the given arXiv ID.")
        else:
            print(f"Failed to fetch details. HTTP Status Code: {response.status_code}")

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