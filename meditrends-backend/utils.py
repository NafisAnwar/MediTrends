# Quick syntax check for utils.py
# If there are any other syntax issues, try this minimal version first

def validate_query(query: str) -> bool:
    """Validate search query"""
    if not query or not isinstance(query, str):
        return False
    query = query.strip()
    if len(query) < 2 or len(query) > 500:
        return False
    import re
    if not re.search(r'[a-zA-Z0-9]', query):
        return False
    return True

def sanitize_query(query: str) -> str:
    """Sanitize search query"""
    if not query:
        return ""
    import re
    sanitized = re.sub(r'[<>"\']', '', query)
    sanitized = re.sub(r'\s+', ' ', sanitized.strip())
    sanitized = re.sub(r'[!@#$%^&*()]{3,}', '', sanitized)
    return sanitized

def validate_sort_parameter(sort: str) -> str:
    """Validate sort parameter"""
    valid_sorts = ['relevance', 'top', 'hot', 'new']
    if sort and sort.lower() in valid_sorts:
        return sort.lower()
    return 'relevance'

def validate_time_filter(time_filter: str) -> str:
    """Validate time filter"""
    valid_filters = ['all', 'year', 'month', 'week', 'day', 'hour']
    if time_filter and time_filter.lower() in valid_filters:
        return time_filter.lower()
    return 'all'

def validate_limit(limit) -> int:
    """Validate limit parameter"""
    try:
        limit_int = int(limit)
        if limit_int < 1:
            return 10
        elif limit_int > 200:
            return 100
        else:
            return limit_int
    except (ValueError, TypeError):
        return 50

def create_api_response(data=None, message="", status="success", status_code=200):
    """Create API response"""
    from datetime import datetime
    response = {
        'status': status,
        'timestamp': datetime.utcnow().isoformat(),
        'status_code': status_code
    }
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return response

def create_error_response(error: str, status_code: int = 400, details=None):
    """Create error response"""
    from datetime import datetime
    response = {
        'status': 'error',
        'error': error,
        'timestamp': datetime.utcnow().isoformat(),
        'status_code': status_code
    }
    if details:
        response['details'] = details
    return response

def validate_environment_variables():
    """Validate environment variables"""
    import os
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET']
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    return missing_vars

def setup_logging(log_level='INFO', log_file=None):
    """Setup logging"""
    import logging
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    root_logger.handlers.clear()
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger

# Minimal functions for other modules
def log_api_request(request_data, response_data, execution_time):
    """Log API request"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"API Request: query={request_data.get('query', '')}, results={len(response_data.get('data', {}).get('results', []))}, time={execution_time:.2f}s")

def format_search_results_for_display(results):
    """Format results for display"""
    return results  # For now, just return as-is