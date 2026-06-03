import os
import json
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from app.core.config import llm
from app.agents.state import AgentState

# --- 1. HELPER FUNCTION: SERPER.DEV SEARCH ---
def search_google_serper(query: str, num_results: int = 10) -> list:
    """Queries Serper.dev to get the top organic Google search results."""
    url = "https://google.serper.dev/search"
    
    # Serper requires a specific JSON payload format
    payload = json.dumps({
      "q": query,
      "num": num_results
    })
    
    headers = {
      'X-API-KEY': os.getenv("SERPER_API_KEY"),
      'Content-Type': 'application/json'
    }
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response_data = response.json()
        
        # We only want the URLs from the "organic" search results
        urls = []
        if "organic" in response_data:
            for item in response_data["organic"]:
                urls.append(item["link"])
        return urls
    except Exception as e:
        print(f"Serper API Error: {e}")
        return []


# --- 2. HELPER FUNCTION: WEB SCRAPING ---
def scrape_website_text(url: str) -> str:
    """Visits a URL and extracts only the readable paragraph text using BeautifulSoup."""
    try:
        # A 5-second timeout prevents the agent from hanging on slow travel blogs
        headers = {'User-Agent': 'Mozilla/5.0'} # Spoofing a browser so we don't get blocked
        response = requests.get(url, headers=headers, timeout=5)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract paragraph text to avoid menus, ads, and footers
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs])
        
        # Return a snippet of the text (e.g., first 3000 characters) to save LLM token costs
        return text[:3000] 
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return ""


# --- 3. FORCE STRICT JSON OUTPUT ---
class AnalystOutput(BaseModel):
    seo_landscape_summary: str = Field(description="A comprehensive summary of what the top competitor articles are currently talking about regarding the topic.")


# --- 4. THE SYSTEM PROMPT ---
analyst_prompt = """You are an expert SEO Researcher for a travel blog.
I will give you a travel topic and the raw text scraped from the top-ranking competitor articles on Google.

Topic: {topic}
Competitor Data: {scraped_data}

Read the competitor data and write a detailed summary of what currently exists. What are they all talking about? What are the common themes? What specific locations, prices, or tips do they mention?
"""


# --- 5. THE MAIN NODE FUNCTION ---
def run_analyst(state: AgentState):
    print("--- 🕵️‍♂️ ANALYST AGENT: SEARCHING GOOGLE VIA SERPER ---")
    topic = state["topic"]
    
    # Step A: Get the top URLs from Serper.dev
    top_urls = search_google_serper(query=topic, num_results=10)
    print(f"Found {len(top_urls)} organic competitor URLs.")
    
    # Step B: Scrape the Competitor Websites
    print("--- 🕵️‍♂️ ANALYST AGENT: SCRAPING COMPETITOR CONTENT ---")
    combined_competitor_text = ""
    
    # We loop through the top 5 URLs to scrape their text.
    # We limit to 5 here so we don't overload the LLM context window.
    for url in top_urls[:5]:
        print(f"Scraping: {url}")
        scraped_text = scrape_website_text(url)
        if scraped_text:
            combined_competitor_text += f"\n\n--- Source: {url} ---\n{scraped_text}"
        
    # Step C: Synthesize the Data using the LLM
    print("--- 🕵️‍♂️ ANALYST AGENT: SYNTHESIZING SEO LANDSCAPE ---")
    structured_llm = llm.with_structured_output(AnalystOutput)
    
    formatted_prompt = analyst_prompt.format(
        topic=topic,
        scraped_data=combined_competitor_text
    )
    
    response = structured_llm.invoke(formatted_prompt)
    
    # Step D: Update the State
    return {
        "search_urls": top_urls,
        "competitor_content": response.seo_landscape_summary
    }