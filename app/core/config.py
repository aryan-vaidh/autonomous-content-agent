# pip install langchain-google-genai

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load the GOOGLE_API_KEY from your .env file
load_dotenv()


# Adding 'max_retries' ensures that if the API is busy, 
# the agent will try up to 3 times before actually giving up.

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    max_retries=3,  # Automatically retries if Google's API is busy
    timeout=60,      # Gives the model extra time for long articles
    google_api_key=os.getenv("GOOGLE_API_KEY")
)