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
    try:
        message_type = response.get('type')

        if message_type == "TRANSCRIPT":
            # Extract the data section for the transcription
            data = response.get('data', [])
            
            # If there's no data, return an error
            if not data:
                return {
                    "result": text,
                    "start_time": 0,
                    "end_time": 0,
                    "err_msg":response.get("err", "No transcription data found ")
                }

            # Assuming the data is nested, access the first item
            data = data[0][0] if isinstance(data[0], list) else data[0]
            
            text = data['text']
            try:
                timestamp = data['timestamp']
            except Exception as e:
                print(f"Error: {e}")

            # If there are no timestamps, use default values (-1, -1)
            if not timestamp:
                return {
                    "result": text,
                    "start_time": 0,
                    "end_time": 0,
                    "err_msg":response.get("err", "No Timestamp Found")
                }

            # Ensure timestamp is a list of lists
            if isinstance(timestamp, list) and all(isinstance(t, list) for t in timestamp):
                start_time = timestamp[0][0]  # First value of the first timestamp list
                end_time = timestamp[-1][-1]  # Last value of the last timestamp list
                
            else:
                return {
                    "result": text,
                    "start_time": 0,
                    "end_time": 0,
                    "err_msg":response.get("err", "Invalid timestamp format.")
                }

            # Return the processed data with text, start time, and end time
            return {
                "result": text,
                "start_time": start_time,
                "end_time": end_time,
                "err_msg":response.get("err", " ")
            }

        elif message_type == "ERROR":
            # Handle the heartbeat message
            print("Error Occurred ")
            return {
                    "result": " ",
                    "start_time": -1,
                    "end_time": -1,
                    "err_msg":response.get("err", " ")
                }

        else:
            return {
                    "result": " ",
                    "start_time": -1,
                    "end_time": -1,
                    "err_msg":response.get("err", "Unknown message type. ")
                }

    except Exception as e:
        # Handle unexpected errors and provide a message
        return {
                    "result": " ",
                    "start_time": -1,
                    "end_time": -1,
                    "err_msg":response.get("err", f"An error occurred: {e}")
                }