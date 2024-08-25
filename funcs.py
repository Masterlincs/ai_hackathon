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
            else:
                print("No entry found for the given arXiv ID.")
        else:
            print(f"Failed to fetch details. HTTP Status Code: {response.status_code}")

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
        "parameters": {"max_length": 500, "num_beams": 5}
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

def generate_random_arxiv_id():
    # Generate a random year and month
    year = random.randint(1991, 2024)  # Adjust as per the arXiv starting year
    month = random.randint(1, 12)
    
    # Create a two-digit month string
    month_str = f"{month:02d}"
    
    # Generate a random paper number (5 digits)
    paper_number = random.randint(1, 99999)
    
    # Create the arXiv ID in the format "yymm.number"
    arxiv_id = f"{str(year)[2:]}{month_str}.{paper_number:05d}"
    
    return arxiv_id

def fetch_random_valid_paper_details():
    while True:
        # Generate a random arXiv ID
        random_arxiv_id = generate_random_arxiv_id()
        print(f"Generated arXiv ID: {random_arxiv_id}")
        
        # Create an ArxivPaper instance
        paper = ArxivPaper(random_arxiv_id)
        
        # Fetch details from arXiv
        if paper.fetch_details():
            return random_arxiv_id
        else:
            return None