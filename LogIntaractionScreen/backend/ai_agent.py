#
# AI Agent logic using LangGraph.
# This file encapsulates the state machine and LLM calls, keeping the API logic clean.
#
import os
from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
from typing import List, Optional, Dict, Any, TypedDict, Annotated
from models import InteractionBase
from datetime import date
from langchain_core.tools import tool
# MODIFIED: Import all necessary DB functions
from db import find_interactions_by_criteria, update_interaction_in_db, get_interaction_by_hcp_and_date

# --- AI Agent Configuration with LangGraph ---
GROQ_API_KEY = "PUT The key here"
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_KEY":
    raise ValueError("GROQ_API_KEY is not set. Please update the code.")

# Initialize the Groq language models
gemma_model = ChatGroq(temperature=0, model="gemma2-9b-it")
llama_model = ChatGroq(temperature=0, model="llama3-70b-8192")

# --- Define the Tools ---
@tool
def fetch_interaction_tool(hcp_name: str, interaction_date: str) -> Dict[str, Any]:
    """
    Fetches interaction records from the database by HCP name and date.
    Use this tool when the user asks to "populate", "find", or "load" a meeting.
    The date must be in YYYY-MM-DD format.
    """
    try:
        interactions = find_interactions_by_criteria(hcp_name, interaction_date)
        
        if not interactions:
            return {"status": "not_found", "data": []}
        
        # We still need the full data for a single match, so we fetch it here.
        full_interaction = get_interaction_by_hcp_and_date(hcp_name, interaction_date)

        if len(interactions) == 1:
            return {"status": "success", "data": full_interaction}
        else:
            # Return summaries for the user to choose from
            return {"status": "multiple_found", "data": interactions}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

# In ai_agent.py
# In ai_agent.py

@tool
def update_interaction_tool(
    interaction_id: Optional[int] = None,
    hcp_name: Optional[str] = None, 
    interaction_date: Optional[str] = None, 
    new_interaction_date: Optional[str] = None, # NEW: Parameter for the updated date
    new_summary: Optional[str] = None,
    new_sentiment: Optional[str] = None,
    new_outcomes: Optional[str] = None,
    new_follow_up: Optional[str] = None,
    new_discussion_topics: Optional[List[str] | str] = None,
) -> str:
    """
    Updates an existing interaction record. Best to use `interaction_id` if available.
    Otherwise, it requires `hcp_name` and `interaction_date` to find the record.
    The new date must be in YYYY-MM-DD format.
    """
    try:
        target_id = interaction_id
        
        if not target_id:
            if not hcp_name or not interaction_date:
                return "To update, I need either the interaction's ID or the HCP name and date."
            records = find_interactions_by_criteria(hcp_name, interaction_date)
            if not records:
                return "Could not find a matching interaction to update."
            if len(records) > 1:
                return "Found multiple interactions. Please be more specific about which one to update."
            target_id = records[0]['id']

        updates = {}
        # NEW: Logic to handle updating the date
        if new_interaction_date is not None: 
            updates['interactionDate'] = new_interaction_date
        
        if new_summary is not None: updates['summary'] = new_summary
        if new_sentiment is not None: updates['sentiment'] = new_sentiment
        if new_outcomes is not None: updates['outcomes'] = new_outcomes
        if new_follow_up is not None: updates['followUp'] = new_follow_up
        
        if new_discussion_topics is not None:
            if isinstance(new_discussion_topics, str):
                updates['discussionTopics'] = [topic.strip() for topic in new_discussion_topics.split(',')]
            else:
                updates['discussionTopics'] = new_discussion_topics
        
        if not updates:
            return "No new data provided to update."
            
        success = update_interaction_in_db(target_id, updates)
        
        return f"Successfully updated interaction with ID {target_id}." if success else f"Failed to update interaction with ID {target_id}."
            
    except Exception as e:
        return f"An error occurred: {e}"
# --- LangGraph Setup for Tool-Calling Agent ---
tools = [fetch_interaction_tool, update_interaction_tool]
agent_with_tools = llama_model.bind_tools(tools)

class AgentState(TypedDict):
    """The state of the conversation graph."""
    messages: Annotated[List[BaseMessage], lambda a, b: a + b]
    interaction_id: Optional[int] # ID for context
    parsed_data: Optional[Dict]
    fetched_data: Optional[Dict]
    tool_output: Optional[str]

def call_agent_with_tools(state: AgentState):
    """Node to call the LLM with tool-calling capabilities."""
    messages = state['messages']
    interaction_id = state.get('interaction_id')
    
    context_note = ""
    if interaction_id:
        context_note = f"\n\n[System note: The user is focused on interaction ID: {interaction_id}. Use this ID for any 'update_interaction_tool' calls.]"

    system_prompt = (
        "You are a highly capable AI assistant for HCP interaction logging. "
        "Your primary function is to interpret user commands and call the appropriate tool. "
        "Strictly follow the user's request and tool descriptions."
        f"{context_note}"
    )
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages")
    ])
    chain = prompt_template | agent_with_tools
    response = chain.invoke({"messages": messages})
    return {"messages": [response]}

def call_tool(state: AgentState):
    """Node to execute the tool chosen by the agent."""
    last_message = state['messages'][-1]
    tool_call = last_message.tool_calls[0]
    tool_name = tool_call['name']
    tool_args = tool_call['args']
    
    if tool_name == 'fetch_interaction_tool':
        tool_result = tools[0].invoke(tool_args)
        return {"messages": [ToolMessage(content=str(tool_result), tool_call_id=tool_call['id'])], "fetched_data": tool_result}
    elif tool_name == 'update_interaction_tool':
        if 'interaction_id' not in tool_args and state.get('interaction_id'):
            tool_args['interaction_id'] = state['interaction_id']
        tool_result = tools[1].invoke(tool_args)
        return {"messages": [ToolMessage(content=tool_result, tool_call_id=tool_call['id'])], "tool_output": tool_result}

def should_continue(state: AgentState) -> str:
    """Conditional edge to determine the next step in the graph."""
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return "call_tool"
    return "end"

tool_workflow = StateGraph(AgentState)
tool_workflow.add_node("agent", call_agent_with_tools)
tool_workflow.add_node("call_tool", call_tool)
tool_workflow.set_entry_point("agent")
tool_workflow.add_conditional_edges("agent", should_continue, {"call_tool": "call_tool", "end": END})
tool_workflow.add_edge("call_tool", END)
tool_runnable = tool_workflow.compile()

# --- Logging Workflow (Unchanged) ---
def call_llm(state: AgentState):
    messages = state['messages']
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a friendly and helpful AI assistant for logging interactions. Respond conversationally and ask clarifying questions to gather details."),
        MessagesPlaceholder(variable_name="messages")
    ])
    chain = prompt_template | gemma_model
    response = chain.invoke({"messages": messages})
    return {"messages": [response]}

def extract_data(state: AgentState):
    messages = state['messages']
    parser = JsonOutputParser(pydantic_object=InteractionBase)
    extraction_prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                """You are an expert data extraction bot. Your task is to extract 
                information about a medical interaction from the provided conversation history.
                Analyze the entire conversation to find details for the following fields: 
                hcpName, summary, date, and sentiment. The 'hcpName' is REQUIRED.
                If the 'hcpName' is missing, return null for that field. Do not invent data.
                The 'date' must be in YYYY-MM-DD format. If missing, use today's date: {current_date}.
                {format_instructions}"""
            ),
            HumanMessagePromptTemplate.from_template("{messages}")
        ],
        partial_variables={"format_instructions": parser.get_format_instructions(), "current_date": date.today().isoformat()}
    )
    extraction_chain = extraction_prompt | llama_model | parser
    try:
        parsed_data = extraction_chain.invoke({"messages": str(messages)})
        if parsed_data and isinstance(parsed_data, dict) and parsed_data.get('hcpName'):
            return {"parsed_data": parsed_data}
        return {"parsed_data": None}
    except Exception as e:
        print(f"Extraction failed: {e}")
        return {"parsed_data": None}

#
# AI Agent logic using LangGraph.
# ... (all existing code is the same) ...
#

# --- Standalone Function for Form Population ---

# NEW: This function is dedicated to parsing a single prompt into form data.
def extract_for_form(text_input: str):
    """
    Parses a single block of unstructured text to extract all possible fields for an interaction.
    """
    parser = JsonOutputParser(pydantic_object=InteractionBase)
    
    extraction_prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                """You are an expert data extraction bot. Your task is to extract 
                information about a medical interaction from the provided text.
                Extract details for ALL of the following fields if present: 
                hcpName, interactionType, interactionDate, summary, discussionTopics, 
                sentiment, outcomes, and followUp.

                Instructions:
                - 'hcpName' is the name of the healthcare professional.
                - 'interactionDate' must be in YYYY-MM-DD format. Use today's date ({current_date}) if not mentioned.
                - 'discussionTopics' should be a list of key topics.
                - 'sentiment' should be a single word: Positive, Neutral, or Negative.
                - For any field that is not mentioned in the text, return null for that field.

                {format_instructions}
                """
            ),
            HumanMessagePromptTemplate.from_template("{text_input}")
        ],
        partial_variables={
            "format_instructions": parser.get_format_instructions(),
            "current_date": date.today().isoformat()
        }
    )
    
    # Use the more powerful model for this complex extraction task
    extraction_chain = extraction_prompt | llama_model | parser
    
    try:
        parsed_data = extraction_chain.invoke({"text_input": text_input})
        return parsed_data
    except Exception as e:
        print(f"Extraction for form failed: {e}")
        return None

log_workflow = StateGraph(AgentState)
log_workflow.add_node("llm", call_llm)
log_workflow.add_node("extract", extract_data)
log_workflow.set_entry_point("llm")
log_workflow.add_edge("llm", "extract")
log_workflow.add_edge("extract", END)
log_runnable = log_workflow.compile()