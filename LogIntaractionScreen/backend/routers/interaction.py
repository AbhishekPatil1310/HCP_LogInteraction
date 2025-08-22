#
# FastAPI Router for handling all API endpoints related to interactions.
#
from datetime import date
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models import InteractionBase, ChatMessage, ChatRequest, PopulateRequest
# MODIFIED: Import the new get_interaction_by_id function
from db import insert_interaction_to_db, update_interaction_in_db, get_all_interactions, get_interaction_by_id, find_interactions_by_criteria
from ai_agent import log_runnable, call_llm, tool_runnable, extract_for_form
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

# Initialize the API router.
router = APIRouter()

# MODIFIED: This endpoint now returns the newly created record.
@router.post("/log-interaction/form")
async def log_form_interaction(interaction: InteractionBase):
    """
    Logs an interaction and returns the newly created record.
    """
    try:
        interaction_data = interaction.model_dump(by_alias=True)
        new_interaction = insert_interaction_to_db(interaction_data, logging_method="form")
        if new_interaction:
            return {"status": "success", "message": "Interaction logged successfully.", "data": new_interaction}
        else:
            raise HTTPException(status_code=500, detail="Failed to create and retrieve new interaction.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log-interaction/chat")
async def log_chat_interaction(request: ChatRequest):
    """
    Logs an interaction and handles the conversation via the AI agent.
    """
    try:
        messages: List[BaseMessage] = []
        for msg in request.chatHistory:
            if msg.sender == "user":
                messages.append(HumanMessage(content=msg.text))
            else:
                messages.append(AIMessage(content=msg.text))
        
        messages.append(HumanMessage(content=request.message))
        
        agent_output = log_runnable.invoke({"messages": messages})
        
        log_data = agent_output.get('parsed_data')
        
        if log_data and log_data.get('hcpName'):
            if 'date' not in log_data or log_data.get('date') is None:
                log_data['interactionDate'] = date.today().isoformat()
            else:
                log_data['interactionDate'] = log_data.pop('date')

            insert_interaction_to_db(log_data, logging_method="chat")
            
            return {"status": "success", "response": "Great! I've got it all saved."}
        
        else:
            llm_response = call_llm({"messages": messages})
            response_message_content = llm_response.get('messages')[-1].content
            
            return {"status": "continue", "response": response_message_content}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

@router.put("/edit-interaction/{interaction_id}")
async def edit_interaction(interaction_id: int, updated_interaction: InteractionBase):
    """
    Updates an existing interaction record in the database.
    """
    try:
        updated_data = updated_interaction.model_dump(by_alias=True, exclude_unset=True)
        success = update_interaction_in_db(interaction_id, updated_data)
        if not success:
            raise HTTPException(status_code=404, detail="Interaction not found.")
        return {"status": "success", "message": "Interaction updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/interactions")
async def get_interactions():
    """
    Retrieves all interaction records.
    """
    try:
        interactions = get_all_interactions()
        return interactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")
        
@router.post("/populate-form-from-chat")
async def populate_form_from_chat(request: ChatRequest):
    """
    Takes a chat message and uses the AI agent's tool to fetch a record from the DB.
    """
    try:
        messages = [HumanMessage(content=request.message)]
        agent_input = {"messages": messages, "interaction_id": request.interactionId}
        agent_output = tool_runnable.invoke(agent_input)
        
        fetched_data = agent_output.get('fetched_data')
        
        if fetched_data:
            return {"status": "success", "data": fetched_data}
        else:
            raise HTTPException(status_code=404, detail="Could not find a matching interaction.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

@router.post("/update-from-chat")
async def update_from_chat(request: ChatRequest):
    """
    Handles a chat-based request to update an existing database record.
    """
    try:
        messages = [HumanMessage(content=request.message)]
        agent_input = {"messages": messages, "interaction_id": request.interactionId}
        agent_output = tool_runnable.invoke(agent_input)
        
        tool_output = agent_output.get('tool_output')
        
        if tool_output:
            return {"status": "success", "response": tool_output}
        else:
            llm_response = agent_output.get('messages', [])[-1]
            return {"status": "continue", "response": llm_response.content}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

@router.post("/extract-and-populate")
async def extract_and_populate_form(request: PopulateRequest):
    """
    Takes an unstructured prompt, extracts interaction details, and returns them as JSON.
    """
    try:
        extracted_data = extract_for_form(request.message)
        if extracted_data and extracted_data.get('hcpName'):
            return {"status": "success", "data": extracted_data}
        else:
            return {"status": "failure", "data": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")