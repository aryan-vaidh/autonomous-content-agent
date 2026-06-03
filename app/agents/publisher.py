import os
import requests
from app.agents.state import AgentState

# --- 1. HELPER FUNCTION: PARSE THE DRAFT ---
def extract_title_and_body(draft_text: str):
    """Splits the Markdown draft into a Title, Meta, and the actual article body."""
    lines = draft_text.split("\n")
    
    # We grab the first line and strip out the "# " to get the clean title
    title = lines[0].replace("# ", "").strip() if lines else "New Travel Post"
    
    # The rest of the text becomes the body
    body = "\n".join(lines[1:]).strip()
    return title, body

# --- 2. THE MAIN NODE FUNCTION ---
def run_publisher(state: AgentState):
    print("--- 🚀 PUBLISHER AGENT: PUSHING TO WIX ---")
    
    if not state.get("is_approved"):
        print("Article was not approved. Aborting publish.")
        return state

    title, body = extract_title_and_body(state["full_article_draft"])
    
    # --- 3. THE WIX API CALL ---
    # This is the official Wix endpoint for creating a blog post
    wix_url = "https://www.wixapis.com/blog/v3/draft-posts"

    # Clean the body of any formatting that Wix V3 might reject
    clean_body = body.replace('**', '').replace('##', '').replace('#', '').strip()
    
    # --- NEW: Wix requires each line to be its own paragraph node ---
    # Split the text by line breaks and ignore any blank lines
    lines = [line.strip() for line in clean_body.split('\n') if line.strip()]
    
    content_nodes = []
    for line in lines:
        content_nodes.append({
            "type": "PARAGRAPH",
            "nodes": [
                {
                    "type": "TEXT",
                    "textData": {
                        "text": line,
                        "decorations": []
                    }
                }
            ]
        })
    
    # Insert the dynamically generated list of nodes into the payload
    payload = {
        "draftPost": {
            "title": title,
            "memberId": "7c9159bb-d004-45a7-8449-a195cb36425e",
            "richContent": {
                "nodes": content_nodes
            }
        }
    }


    headers = {
        "Authorization": os.getenv("WIX_API_KEY"),
        "wix-site-id": os.getenv("WIX_SITE_ID"),
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(wix_url, json=payload, headers=headers)
        response.raise_for_status()
        print("✅ Successfully published to Wix!")
        
        # --- THE FINAL SLACK NOTIFICATION ---
        slack_token = os.getenv("SLACK_BOT_TOKEN")
        slack_channel = "#mysterioustrip" 
        
        slack_headers = {"Authorization": f"Bearer {slack_token}"}
        slack_payload = {
            "channel": slack_channel,
            "text": f"🎉 *Success!* I just pushed _{title}_ to your Wix dashboard. Go check it out!"
        }
        requests.post("https://slack.com/api/chat.postMessage", json=slack_payload, headers=slack_headers)

    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to publish to Wix: {e}")
        # THIS IS THE GOLDEN TICKET: Prints the exact reason Wix rejected it
        print(f"🔍 WIX ERROR DETAILS: {e.response.text}") 
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        
    return state