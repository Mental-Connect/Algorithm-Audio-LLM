import json
import logging

logger = logging.getLogger(__name__)

async def baidu_processing(response):
    try:
        logger.info(f"Processing response: {response} (Type: {type(response)})")
        
        # If response is a list, handle it accordingly
        if isinstance(response, list):
            # Assuming the list contains dictionaries, process the first item in the list
            if len(response) > 0 and isinstance(response[0], dict):
                res_data = response[0]  # Process the first dictionary in the list
            else:
                # If the list doesn't contain a dictionary, handle as needed
                logger.error(f"List doesn't contain a dictionary: {response}")
                return None
        elif isinstance(response, dict):
            # If it's already a dictionary, use it directly
            res_data = response
        elif isinstance(response, str):
            # If it's a string, try to parse it as JSON
            res_data = json.loads(response)
        else:
            # Handle unexpected types
            logger.error(f"Unexpected response type: {type(response)}. Cannot process.")
            return None
        
        # Now process the response as expected
        if res_data.get("type") == "HEARTBEAT":
            return {
                "result": "HEARTBEAT",
                "start_time": 0,
                "end_time": 0,
                "err_msg": "Ping"
            }
        
        if res_data.get("type") == "FINISH":
            return {
                "result": "FINISH",
                "start_time": 0,
                "end_time": 0,
                "err_msg": "Process finished"
            }

        # If not heartbeat, process the regular response
        else:
            return {
                "result": res_data.get("result", ""),
                "start_time": res_data.get("start_time", 0),
                "end_time": res_data.get("end_time", 0),
                "err_msg": res_data.get("err_msg", "")
            }
    
    except json.JSONDecodeError:
        logger.error("Error parsing the response JSON")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in processing: {e}")
        return None 



async def offline_processing(response):
    return response