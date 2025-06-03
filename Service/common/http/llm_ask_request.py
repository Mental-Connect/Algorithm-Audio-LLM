from pydantic import BaseModel

# Define a Pydantic model to validate and serialize input data for chatbot requests
class LLMAskRequest:    
    # The context or background information to assist the chatbot in understanding the query
    context: str
    
    query: str
    
    user_id: str
    
    school_id: str