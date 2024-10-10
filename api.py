from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import whois
from urllib.parse import urlparse
import numpy as np
import pickle
import ipaddress
import re
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Load the pre-trained model
with open('phishing_classifier.pkl', 'rb') as pick_file:
    model = pickle.load(pick_file)

class URLInput(BaseModel):
    url: str

class FeatureExtract:
    def isIP(self, url):
        try:
            ipaddress.ip_address(url)
            return 1
        except ValueError:
            return 0

    def isat(self, url):
        return 1 if "@" in url else 0

    def isRedirect(self, url):
        pos = url.rfind('//')
        return 1 if pos > 6 else 0

    def haveDash(self, url):
        return 1 if '-' in urlparse(url).netloc else 0

    def no_sub_domain(self, url):
        url = url.replace("www.", "")
        url = url.replace("." + urlparse(url).netloc.split('.')[-1], "")
        count = url.count(".")
        return 0 if count == 1 else 1

    def LongURL(self, url):
        return 1 if len(url) >= 54 else 0

    def tinyURL(self, url):
        shortening_services = r"bit\.ly|goo\.gl|t\.co|tinyurl"
        return 1 if re.search(shortening_services, url) else 0

# Create a new class that checks domain
@app.post("/check/")
def check_url(url_input: URLInput):
    url = url_input.url
    feature_extract = FeatureExtract()
    features = [
        feature_extract.isIP(url),
        feature_extract.isat(url),
        feature_extract.isRedirect(url),
        feature_extract.haveDash(url),
        feature_extract.no_sub_domain(url),
        feature_extract.LongURL(url),
        feature_extract.tinyURL(url)
    ]

    features_np = np.array(features).reshape((1, -1))
    prediction = model.predict(features_np)
    
    result = "Legitimate" if prediction[0] == 0 else "Phishing"
    return {"url": url, "classification": result}

# Start FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
