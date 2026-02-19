import logging
import random

from langgraph.graph import END, START, StateGraph

from src.graphs.state import GraphState

logger = logging.getLogger(__name__)

def process_input(state: GraphState) -> dict:
    """
    Initial processing node. Logs the input for traceability.
    """
    input_text = state.get("input", "")
    logger.info(f"Processing input: {input_text}")
    return {}

def route_logic(state: GraphState) -> str:
    """
    Conditional edge logic that branches based on a random dynamic value.
    """
    decision = random.randint(0, 1)
    logger.info(f"Random decision: {decision}")
    
    if decision == 0:
        return "world"
    else:
        return "universe"

def world_node(state: GraphState) -> dict:
    """
    Terminal state resulting in "Hello World".
    """
    return {"message": "Hello World"}

def universe_node(state: GraphState) -> dict:
    """
    Terminal state resulting in "Hello Universe".
    """
    return {"message": "Hello Universe"}

def create_graph():
    """
    Creates and compiles the WriterGraph.
    """
    workflow = StateGraph(GraphState)
    
    workflow.add_node("process_input", process_input)
    workflow.add_node("world_node", world_node)
    workflow.add_node("universe_node", universe_node)
    
    workflow.add_edge(START, "process_input")
    
    # Add conditional edge from process_input
    workflow.add_conditional_edges(
        "process_input",
        route_logic,
        {
            "world": "world_node",
            "universe": "universe_node"
        }
    )
    
    workflow.add_edge("world_node", END)
    workflow.add_edge("universe_node", END)
    
    return workflow.compile()
