import requests
from bs4 import BeautifulSoup

def load_from_url(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    return soup.get_text()

def load_text(text):
    return text