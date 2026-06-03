from typing import TypedDict, List

# We use TypedDict to strictly define the "memory structure" of our graph.
# Every agent in the pipeline will read from and write to this single dictionary.
class AgentState(TypedDict):
    
    # --- CORE INPUT ---
    topic: str                # The travel topic you send via Slack (e.g., "Best time to visit Jaipur")
    
    # --- RESEARCH PHASE (Analyst Memory) ---
    search_urls: List[str]    # A list to store the top 10-20 Google ranking URLs found by Tavily
    competitor_content: str   # The massive string of combined text scraped from those competitor websites
    
    # --- STRATEGY PHASE (Strategist Memory) ---
    strategist_gaps: str      # The analysis of what the top articles missed (your unique Mysterioustrip angle)
    
    # --- WRITING PHASE (Writer Memory) ---
    full_article_draft: str   # The completed, full-length SEO-optimized article ready for review
    
    # --- APPROVAL PHASE (Human-in-the-Loop) ---
    is_approved: bool         # A true/false flag. False = wait for your approval. True = ready to publish!