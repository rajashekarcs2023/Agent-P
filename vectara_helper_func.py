### Write code for the new module here and import it from agent.py.
import json
import requests


CORPUS_KEY = "agentp"

standard_headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'x-api-key': VECTARA_API_KEY
}

async def create_chat(query, ctx):
    url = "https://api.vectara.io/v2/chats"
    
    payload = {
        "query": query,
        "search": {
            "corpora": [
                {
                    "corpus_key": CORPUS_KEY,
                    "semantics": "default"  # Using default semantics without any advanced settings
                }
            ],
            "offset": 0,
            "limit": 5  # Limiting to 5 results as a basic feature
        },
        "chat": {
            "store": True  # Store the chat message and response
        }
    }

    # Log the payload before the request, without serializing `ctx`
    ctx.logger.info(f"Sending request to Vectara with payload: {json.dumps(payload)}")
    
    headers = standard_headers
    
    try:
        response = requests.post(url, headers=headers, json=payload) 

        # Log the full response details for debugging
        ctx.logger.info(f"Response status code: {response.status_code}")
        ctx.logger.info(f"Response body: {response.text}")

        if response.status_code == 200:
            chat_data = response.json()
            ctx.logger.info(f"Chat created successfully with ID: {chat_data['chat_id']}")
            return chat_data['chat_id'],chat_data['answer']
        else:
            ctx.logger.info(f"Failed to create chat. Status Code: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        ctx.logger.info(f"An error occurred while trying to create a chat: {e}")
        return None

async def add_turn(chat_id, query, ctx):
    url = f"https://api.vectara.io/v2/chats/{chat_id}/turns"
    
    payload = {
        "query": query,
        "search": {
            "corpora": [
                {
                    "corpus_key": CORPUS_KEY,
                    "semantics": "default"
                }
            ],
            "offset": 0,
            "limit": 5  # Limiting to 5 results
        }
    }
    
    headers = standard_headers
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        ctx.logger.info(str(f"Response status code: {response.status_code}"))
        ctx.logger.info(str(f"Response body: {response.text}"))

        if response.status_code == 200:
            turn_data = response.json()
            ctx.logger.info(f"Turn added successfully. Turn ID: {turn_data['turn_id']}")

            # Return the 'answer' if available
            if 'answer' in turn_data:
                ctx.logger.info(f"Response from chat: {turn_data['answer']}")
                return turn_data['answer']
            else:
                ctx.logger.info(f"No answer returned in the response. Full response: {turn_data}")
                return "No answer returned"
        else:
            ctx.logger.info(f"Failed to add turn. Status Code: {response.status_code}, Response: {response.text}")
            return f"Error: {response.status_code}"
    except Exception as e:
        ctx.logger.info(f"An error occurred while trying to add a turn: {e}")
        return f"An error occurred: {e}"
