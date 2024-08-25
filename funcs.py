import requests
import xml.etree.ElementTree as ET
import random

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
                
                return True
        return False
    
    def display_details(self):
        print(f"Title: {self.title}")
        print("Authors: ", ", ".join(self.authors))
        print(f"Summary: {self.summary}")


def summarise_blurb(blurb, api_key):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": blurb,
        "parameters": {"max_length": 500, "min_length": 50}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()[0]['summary_text']

def write_new_blurb(blurb_summary, api_key):
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": blurb_summary,
        "parameters": {"max_length": len(blurb_summary)+150, "num_beams": 5, "min_length":len(blurb_summary)-50}
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

def is_valid_api_key(api_key: str) -> bool:
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    response = requests.get("https://huggingface.co/api/whoami-v2", headers=headers)
    
    # If the status code is 200, the API key is valid
    if response.status_code == 200:
        return True
    else:
        return False


previous_ids = set()

def generate_random_arxiv_id():
    # Generate a random arXiv ID with realistic formatting
    year = random.choice(['22', '23'])  # Choose a year (last two digits)
    month = random.randint(1, 12)
    month_str = f"{month:02d}"
    paper_number = random.randint(1, 99999)  # Allow up to 5 digits for realistic ID
    
    arxiv_id = f"{year}{month_str}.{paper_number:05d}"
    return arxiv_id

def fetch_random_valid_paper_details():
    while True:
        random_arxiv_id = generate_random_arxiv_id()
        if random_arxiv_id not in previous_ids:
            previous_ids.add(random_arxiv_id)
            paper = ArxivPaper(random_arxiv_id)
            if paper.fetch_details():
                paper.display_details()
                return random_arxiv_id
        print(f"Invalid arXiv ID: {random_arxiv_id}, retrying...")