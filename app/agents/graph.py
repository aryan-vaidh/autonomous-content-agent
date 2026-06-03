import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from app.agents.state import AgentState
from app.agents.analyst import run_analyst
from app.agents.strategist import run_strategist
from app.agents.writer import run_writer
from app.agents.publisher import run_publisher # <--- Import the REAL publisher

# # --- REMOVE THE DUMMY NODE ---
# # --- 1. PLACEHOLDER PUBLISHER NODE ---
# # We will build this fully in Phase 5, but we need it here now 
# # so the graph knows where to go AFTER you hit approve.
# def run_publisher(state: AgentState):
#     print("--- 🚀 PUBLISHER AGENT: PUSHING TO WIX ---")
#     if state.get("is_approved"):
#         print("Article approved! Publishing to Mysterioustrip...")
#     else:
#         print("Article rejected. Skipping publish.")
#     return state


def build_graph():
    workflow = StateGraph(AgentState)
    
    # 2. Add our nodes
    workflow.add_node("analyst", run_analyst)
    workflow.add_node("strategist", run_strategist)
    workflow.add_node("writer", run_writer)
    workflow.add_node("publisher", run_publisher) # Now using the imported file



    # # --- TRIAL CHANGE: Start at Writer ---
    # workflow.set_entry_point("writer") # Skip Analyst and Strategist for now
    # workflow.add_edge("writer", "publisher")
    # workflow.add_edge("publisher", END)



    # 3. Define the exact execution order
    workflow.set_entry_point("analyst")           
    workflow.add_edge("analyst", "strategist")    
    workflow.add_edge("strategist", "writer")     
    workflow.add_edge("writer", "publisher")      # Writer passes to Publisher
    workflow.add_edge("publisher", END)           
    
    # --- 4. THE MAGIC: CHECKPOINTING & INTERRUPTS ---
    # We create a local SQLite database file to save the graph's memory.
    conn = sqlite3.connect("agent_memory.sqlite", check_same_thread=False)
    memory = SqliteSaver(conn)
    
    # We compile the graph, passing in the memory saver, and explicitly tell it
    # to FREEZE execution right before the "publisher" node starts.
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["publisher"] 
    )

content_graph = build_graph()