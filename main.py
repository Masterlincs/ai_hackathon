from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer

def summarise_blurb(blurb):
    summariser = pipeline("summarization", model="facebook/bart-large-cnn")
    return summariser(blurb, max_length=200, min_length=50)

def write_new_blurb(blurb_summary):
    id = "mistralai/Mistral-7B-Instruct-v0.2"
    model = AutoModelForCausalLM.from_pretrained(id)
    tokenizer = AutoTokenizer.from_pretrained(id)
    input_ids = tokenizer(blurb_summary, return_tensors="pt").input_ids
    text =  model.generate(input_ids, max_length=200, num_beams=5)
    return tokenizer.decode(text[0], skip_special_tokens=True)

def compare_blurbs(blurb, ai_blurb):

    model = SentenceTransformer("all-MiniLM-L6-v2")
    blurbs = [blurb, ai_blurb]

    embeddings = model.encode(blurbs)
    #print(embeddings.shape)

    similarities = model.similarity(embeddings, embeddings)
    #print(similarities)


