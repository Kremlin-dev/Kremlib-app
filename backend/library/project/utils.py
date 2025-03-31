from rest_framework.response import Response
from rest_framework import status


def standard_response(data=None, message=None, status_code=status.HTTP_200_OK, errors=None, **kwargs):
    """
    Standardize API responses across the application.
    
    Args:
        data: The main data payload to return
        message: A human-readable message about the response
        status_code: HTTP status code for the response
        errors: Any errors to include in the response
        **kwargs: Additional key-value pairs to include in the response
    
    Returns:
        Response: A standardized DRF Response object
    """
    response_data = {
        'status': 'success' if status.is_success(status_code) else 'error',
        'message': message or ('Success' if status.is_success(status_code) else 'Error'),
    }
    
    # Add data if provided
    if data is not None:
        response_data['data'] = data
    
    # Add errors if provided
    if errors is not None:
        response_data['errors'] = errors
    
    # Add any additional key-value pairs
    response_data.update(kwargs)
    
    return Response(response_data, status=status_code)


def paginated_response(paginator, serializer_data, message=None, **kwargs):
    """
    Create a standardized response for paginated data.
    
    Args:
        paginator: The paginator instance used
        serializer_data: The serialized data
        message: Optional message to include
        **kwargs: Additional key-value pairs to include
    
    Returns:
        Response: A standardized paginated response
    """
    pagination_data = {
        'count': paginator.page.paginator.count,
        'next': paginator.get_next_link(),
        'previous': paginator.get_previous_link(),
        'results': serializer_data
    }
    
    return standard_response(
        data=pagination_data,
        message=message or 'Data retrieved successfully',
        **kwargs
    )
