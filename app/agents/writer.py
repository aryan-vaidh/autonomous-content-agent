from pydantic import BaseModel, Field
from app.core.config import llm
from app.agents.state import AgentState

# --- 1. FORCE STRICT JSON OUTPUT ---
# We split the output into Title, Meta, and Body so we can format it perfectly.
class WriterOutput(BaseModel):
    title: str = Field(description="An SEO-optimized, highly clickable title for the blog post.")
    meta_description: str = Field(description="A 150-160 character SEO meta description summarizing the article.")
    article_body: str = Field(description="The full, comprehensive travel article written in Markdown format, including H2/H3 tags and bullet points.")


# --- 2. THE SYSTEM PROMPT ---
writer_prompt = """You are an expert Travel Writer and SEO specialist for the blog 'Mysterioustrip'.
Your task is to write a massive, highly engaging, and SEO-optimized travel article.

Topic: {topic}
Strategic Angle & Content Gaps to Fill: {strategy}

Guidelines:
1. Tone: Adventurous, authentic, and highly informative.
2. Format: Use Markdown. Include catchy H2 and H3 headers. Use bullet points for readability.
3. Content: You MUST include the unique angles and missing information identified in the strategy.
4. Depth: Make it comprehensive. Include practical details like estimated costs, best times to visit, local transport, or hidden gems.

Write the complete article now.
"""


# --- 3. THE MAIN NODE FUNCTION ---
def run_writer(state: AgentState):
    print("--- ✍️ WRITER AGENT: CRAFTING THE SEO ARTICLE ---")
    
    structured_llm = llm.with_structured_output(WriterOutput)
    
    # Format the prompt with the topic and the Strategist's gap analysis
    formatted_prompt = writer_prompt.format(
        topic=state["topic"],
        strategy=state["strategist_gaps"]
    )
    
    # Generate the full article
    response = structured_llm.invoke(formatted_prompt)
    
    # Assemble the final draft into a single beautifully formatted string
    # We include the Meta Description at the top so you can review it in Slack
    final_draft = f"# {response.title}\n\n"
    final_draft += f"**Meta Description:** _{response.meta_description}_\n\n"
    final_draft += f"---\n\n"
    final_draft += response.article_body
    
    # Return the final draft to update the state, preparing it for Slack approval
    return {"full_article_draft": final_draft}




# # --- TRIAL MODE: WRITER GENERATING QUICK DRAFT ---
# def run_writer(state: AgentState):
#     print("--- ✍️ TRIAL MODE: WRITER GENERATING QUICK DRAFT ---")
    
#     structured_llm = llm.with_structured_output(WriterOutput)
    
#     # We create a simple prompt that only needs the 'topic' from the state
#     trial_prompt = f"""Write a short, engaging travel blog post about: {state['topic']}.
#     Include a Title, a Meta Description, and a 3-paragraph article body with Markdown headers."""
    
#     response = structured_llm.invoke(trial_prompt)
    
#     final_draft = f"# {response.title}\n\n"
#     final_draft += f"**Meta Description:** _{response.meta_description}_\n\n"
#     final_draft += f"---\n\n"
#     final_draft += response.article_body
    
#     return {"full_article_draft": final_draft}