import json
import logging
from typing import Any, Dict, Optional
import requests
import os
from requests.exceptions import RequestException

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class APIError(Exception):
    """Custom exception for API related errors"""
    pass

def make_post_request(phone_number: str, custom_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make request to warm transfer API
    
    Args:
        phone_number: Customer's phone number
        custom_data: Additional data to send
        
    Returns:
        API response as dictionary
        
    Raises:
        APIError: If the API request fails
    """
    try:
        api_key = os.getenv('BRAINBASE_API_KEY')
        if not api_key:
            raise APIError("Missing API key")

        response = requests.post(
            url='https://uyxceqsk5d.execute-api.us-east-1.amazonaws.com/default/warm_transfer_api',
            headers={
                'x-api-key': api_key,
                'Content-Type': 'application/json'
            },
            json={
                'phone_number': phone_number,
                'data': custom_data
            },
            timeout=5  # 5 second timeout
        )
        response.raise_for_status()
        return response.json()
        
    except RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        raise APIError(f"API request failed: {str(e)}")

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for Amazon Connect events
    
    Args:
        event (dict): The event data from Amazon Connect
        context (object): Lambda context object
    
    Expected Parameters:
        The following parameters can be set in the Amazon Connect contact flow:
        - customer_phone_number (str): Customer's phone number
        - requestType (str): Type of customer request ('post' or 'get')
        - customData (dict): Additional data to send
    
    Returns:
        dict: Response object containing status and any relevant data
    """
    try:
        logger.info('Received event: %s', json.dumps(event))
        
        contact_data: Dict[str, Any] = event.get('Details', {})
        parameters: Dict[str, Any] = contact_data.get('Parameters', {})
        
        # Validate required parameters
        phone_number = contact_data.get('ContactData', {}).get('CustomerEndpoint', {}).get('Address')
        if not phone_number:
            raise ValueError("Missing phone number in request")
            
        custom_data = parameters.get('customData')
        if not custom_data:
            logger.warning("No custom data provided")
            custom_data = {}
            
        request_type = parameters.get('requestType')
        if not request_type:
            raise ValueError("Missing requestType parameter")

        if request_type == 'post':
            api_response = make_post_request(phone_number, custom_data)
            response_data = {
                'api_response': api_response,
                'message': 'Successfully processed POST request'
            }
            
        elif request_type == 'get':
            # Implement GET logic here
            response_data = {
                'message': 'GET request not implemented'
            }
            
        else:
            raise ValueError(f"Invalid requestType: {request_type}")

        response: Dict[str, Any] = {
            'statusCode': 200,
            'body': {
                **response_data,
                'parameters': parameters
            }
        }
        
        logger.info('Response: %s', json.dumps(response))
        return response
        
    except (ValueError, APIError) as e:
        logger.error('Validation/API error: %s', str(e))
        return {
            'statusCode': 400,
            'body': {
                'message': 'Request validation or API error',
                'error': str(e)
            }
        }
        
    except Exception as e:
        logger.error('Unexpected error: %s', str(e), exc_info=True)
        return {
            'statusCode': 500,
            'body': {
                'message': 'Internal server error',
                'error': str(e)
            }
        }


# if __name__ == '__main__':
#     r = requests.post(
#         url='https://uyxceqsk5d.execute-api.us-east-1.amazonaws.com/default/warm_transfer_api',
#         headers={
#             'x-api-key': f'{os.getenv('BRAINBASE_API_KEY')}',
#             'Content-Type': 'application/json'
#         },
#         json={
#             'phone_number': "+14154650216",
#             'data': {"test": "test"}
#         }
#     )

#     print(r.json())