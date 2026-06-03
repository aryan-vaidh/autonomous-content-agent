import json
import uuid
from fastapi import FastAPI, BackgroundTasks, Form, Request
import httpx
from app.agents.graph import content_graph

app = FastAPI(title="Mysterioustrip Content Agent")

# --- 1. BACKGROUND TASK: RUN AGENT & SEND SLACK BUTTONS ---
async def run_agent_and_ask_approval(topic: str, response_url: str):
    print(f"\n🚀 Starting pipeline for: {topic}")
    
    # We generate a unique ID for this specific article run.
    # This thread_id is how LangGraph remembers THIS specific workflow in SQLite!
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {"topic": topic, "is_approved": False}
    
    # Run the graph. It will execute Analyst -> Strategist -> Writer and then STOP.
    result = content_graph.invoke(initial_state, config=config)
    
    # Extract the drafted article from the paused state
    draft = result.get("full_article_draft", "Error: Draft failed.")
    
    # --- SLACK BLOCK KIT UI ---
    # This JSON structure tells Slack to render nice interactive buttons
    slack_payload = {
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Draft Ready for: {topic}*\n\n{draft[:2500]}..."} # Truncated for Slack limits
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Approve & Publish"},
                        "style": "primary",
                        "value": json.dumps({"action": "approve", "thread_id": thread_id}) # We hide the thread_id inside the button!
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "❌ Reject"},
                        "style": "danger",
                        "value": json.dumps({"action": "reject", "thread_id": thread_id})
                    }
                ]
            }
        ]
    }
    
    # Send the interactive message to Slack
    async with httpx.AsyncClient() as client:
        await client.post(response_url, json=slack_payload)


# --- 2. ENDPOINT: SLACK SLASH COMMAND (/draft-article) ---
@app.post("/slack/research")
async def slack_research(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    response_url: str = Form(...)
):
    print(f"📥 Received Slack Command for topic: {text}")
    # Start the research asynchronously so Slack doesn't time out
    background_tasks.add_task(run_agent_and_ask_approval, text, response_url)
    return {"response_type": "in_channel", "text": f"🕵️‍♂️ *Researching top 10 competitors for:* `{text}`. I'll ping you when the draft is ready!"}


# --- 3. NEW ENDPOINT: SLACK INTERACTIVITY (Button Clicks) ---
# When you click a button in Slack, Slack sends a POST request here.
@app.post("/slack/interactions")
async def slack_interactions(request: Request, background_tasks: BackgroundTasks):
    form_data = await request.form()
    # Slack hides the button click data inside a 'payload' JSON string
    payload = json.loads(form_data.get("payload"))
    
    # Extract the action (approve/reject) and the thread_id
    action_data = json.loads(payload["actions"][0]["value"])
    action = action_data["action"]
    thread_id = action_data["thread_id"]
    response_url = payload["response_url"] # Where to send the reply
    
    config = {"configurable": {"thread_id": thread_id}}
    
    if action == "approve":
        print(f"✅ User approved thread: {thread_id}")
        
        # Update the graph's memory to set is_approved to True
        content_graph.update_state(config, {"is_approved": True})
        
        # WAKE THE GRAPH UP! Calling invoke with None tells it to resume from where it paused.
        # We put this in a background task so we can immediately respond to Slack.
        background_tasks.add_task(content_graph.invoke, None, config)
        
        # Immediately replace the buttons in Slack with a success message
        return {"replace_original": "true", "text": "🚀 Article approved! Publishing to Mysterioustrip now..."}
        
    elif action == "reject":
        print(f"❌ User rejected thread: {thread_id}")
        return {"replace_original": "true", "text": "🛑 Draft rejected. The workflow has been terminated."}