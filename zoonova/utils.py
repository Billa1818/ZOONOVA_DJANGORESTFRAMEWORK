from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Handler d'exceptions personnalisé pour des messages d'erreur uniformes
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'message': 'Une erreur est survenue',
            'details': response.data
        }
        
        response.data = custom_response_data
    
    return response
