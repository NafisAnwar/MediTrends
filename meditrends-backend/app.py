"""
MediTrends Backend - Enhanced Flask Application with ML and Async
A Reddit-powered medical trends search engine with lightning-fast performance
"""

import os
import time
import logging
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json

# Import our modules
from config import get_config
from search_engine import EnhancedSearchEngine
from reddit_client import RedditClient
from utils import (
    validate_query, sanitize_query, validate_sort_parameter,
    validate_time_filter, validate_limit, create_api_response,
    create_error_response, log_api_request, format_search_results_for_display,
    validate_environment_variables, setup_logging
)

# Setup logging
setup_logging(log_level='INFO')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, origins=['http://localhost:3000', 'http://localhost:8080', 'http://127.0.0.1:3000'])

# Load configuration
config = get_config()

# Initialize enhanced search engine (lazy loading)
search_engine = None
async_loop = None

def get_search_engine():
    """Get enhanced search engine instance"""
    global search_engine
    if search_engine is None:
        try:
            search_engine = EnhancedSearchEngine()
            logger.info("Enhanced search engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize search engine: {str(e)}")
            raise
    return search_engine

def get_event_loop():
    """Get or create async event loop"""
    global async_loop
    if async_loop is None:
        async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(async_loop)
    return async_loop

def startup_checks():
    """Perform startup checks and validation"""
    logger.info("Starting MediTrends Backend (Enhanced Version)...")
    
    # Check environment variables
    missing_vars = validate_environment_variables()
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file")
    
    # Validate configuration
    try:
        config.validate_config()
        logger.info("Configuration validation passed")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {str(e)}")
    
    # Check Redis availability
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379)
        r.ping()
        logger.info("Redis cache available - searches will be lightning fast!")
    except:
        logger.warning("Redis not available - using in-memory cache (install Redis for better performance)")
    
    logger.info("MediTrends Enhanced Backend startup complete")

# Run startup checks
startup_checks()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint"""
    try:
        reddit_status = "not_tested"
        ml_status = "not_loaded"
        redis_status = "not_available"
        
        if search_engine:
            # Check Reddit
            reddit_health = search_engine.reddit_client.health_check()
            reddit_status = reddit_health.get('status', 'unknown')
            
            # Check ML models
            ml_status = "loaded" if search_engine.sentence_model else "not_loaded"
            
            # Check Redis
            redis_status = "available" if search_engine.redis_enabled else "not_available"
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0',
            'reddit_api_status': reddit_status,
            'ml_models_status': ml_status,
            'redis_cache_status': redis_status,
            'environment': config.FLASK_ENV,
            'features': {
                'async_search': True,
                'ml_scoring': True,
                'semantic_search': True,
                'trending_topics': True,
                'smart_caching': True
            }
        }
        
        return jsonify(create_api_response(data=health_data, message="API is healthy"))
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify(create_error_response(f"Health check failed: {str(e)}", 500)), 500

@app.route('/api/search', methods=['GET', 'POST'])
def search_posts():
    """Enhanced search endpoint with async and ML capabilities"""
    start_time = time.time()
    
    try:
        # Get request data
        if request.method == 'POST':
            request_data = request.get_json() or {}
        else:
            request_data = request.args.to_dict()
        
        # Extract parameters
        query = request_data.get('q', '').strip()
        sort = validate_sort_parameter(request_data.get('sort', 'relevance'))
        time_filter = validate_time_filter(request_data.get('time_filter', 'all'))
        limit = validate_limit(request_data.get('limit', 50))
        format_type = request_data.get('format', 'standard')
        use_ml = request_data.get('use_ml', 'true').lower() == 'true'
        
        # Validate query
        if not validate_query(query):
            return jsonify(create_error_response(
                "Invalid query. Query must be 2-500 characters.",
                400
            )), 400
        
        # Sanitize query
        clean_query = sanitize_query(query)
        
        logger.info(f"Enhanced search request: query='{clean_query}', ML={use_ml}")
        
        # Initialize search engine
        engine = get_search_engine()
        
        # Run async search in sync context
        loop = get_event_loop()
        search_results = loop.run_until_complete(
            engine.search_async(
                query=clean_query,
                sort=sort,
                time_filter=time_filter,
                limit=limit,
                use_ml=use_ml
            )
        )
        
        # Check if search was successful
        if search_results.get('status') == 'error':
            return jsonify(create_error_response(
                search_results.get('metadata', {}).get('error', 'Search failed'),
                500
            )), 500
        
        # Format results if requested
        if format_type == 'display':
            search_results['results'] = format_search_results_for_display(
                search_results.get('results', [])
            )
        
        # Calculate execution time
        execution_time = time.time() - start_time
        search_results['metadata']['api_execution_time'] = execution_time
        
        # Log request
        log_api_request(
            request_data={
                'query': clean_query,
                'sort': sort,
                'limit': limit,
                'use_ml': use_ml
            },
            response_data=search_results,
            execution_time=execution_time
        )
        
        return jsonify(create_api_response(
            data=search_results,
            message=f"Found {len(search_results.get('results', []))} results in {execution_time:.2f}s"
        ))
    
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Search endpoint error: {str(e)}")
        
        return jsonify(create_error_response(
            f"Internal server error: {str(e)}",
            500,
            {'execution_time': execution_time}
        )), 500

@app.route('/api/trending', methods=['GET'])
def get_trending_topics():
    """Get current trending health topics"""
    try:
        engine = get_search_engine()
        
        limit = validate_limit(request.args.get('limit', 10))
        
        trending_topics = engine.trending_tracker.get_trending(limit)
        
        return jsonify(create_api_response(
            data={'trending_topics': trending_topics},
            message=f"Found {len(trending_topics)} trending topics"
        ))
    
    except Exception as e:
        logger.error(f"Trending endpoint error: {str(e)}")
        return jsonify(create_error_response(f"Failed to get trending topics: {str(e)}", 500)), 500

@app.route('/api/search/stream', methods=['POST'])
def search_stream():
    """Streaming search endpoint for real-time results"""
    def generate():
        try:
            request_data = request.get_json() or {}
            query = sanitize_query(request_data.get('q', '').strip())
            
            if not validate_query(query):
                yield json.dumps({'error': 'Invalid query'}) + '\n'
                return
            
            engine = get_search_engine()
            
            # Send initial acknowledgment
            yield json.dumps({
                'status': 'started',
                'query': query,
                'timestamp': datetime.utcnow().isoformat()
            }) + '\n'
            
            # Run search with progress updates
            loop = get_event_loop()
            
            # Quick results first (from cache or top subreddits)
            quick_results = loop.run_until_complete(
                engine.search_async(
                    query=query,
                    limit=10,
                    use_ml=False
                )
            )
            
            yield json.dumps({
                'status': 'quick_results',
                'results': quick_results.get('results', [])[:5],
                'timestamp': datetime.utcnow().isoformat()
            }) + '\n'
            
            # Full ML-enhanced results
            full_results = loop.run_until_complete(
                engine.search_async(
                    query=query,
                    limit=50,
                    use_ml=True
                )
            )
            
            yield json.dumps({
                'status': 'complete',
                'results': full_results.get('results', []),
                'metadata': full_results.get('metadata', {}),
                'timestamp': datetime.utcnow().isoformat()
            }) + '\n'
            
        except Exception as e:
            yield json.dumps({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }) + '\n'
    
    return Response(generate(), mimetype='application/x-ndjson')

@app.route('/api/analyze', methods=['POST'])
def analyze_query():
    """Analyze a query to understand intent and extract entities"""
    try:
        request_data = request.get_json() or {}
        query = request_data.get('q', '').strip()
        
        if not query:
            return jsonify(create_error_response("Query is required", 400)), 400
        
        engine = get_search_engine()
        
        # Run ML analysis
        loop = get_event_loop()
        analysis = loop.run_until_complete(
            loop.run_in_executor(None, engine._analyze_query_ml, query)
        )
        
        # Remove embedding from response (too large)
        if 'query_embedding' in analysis:
            analysis['query_embedding'] = 'Generated (hidden for size)'
        
        return jsonify(create_api_response(
            data={'analysis': analysis},
            message="Query analyzed successfully"
        ))
    
    except Exception as e:
        logger.error(f"Analysis endpoint error: {str(e)}")
        return jsonify(create_error_response(f"Failed to analyze query: {str(e)}", 500)), 500

@app.route('/api/performance', methods=['GET'])
def get_performance_stats():
    """Get search performance statistics"""
    try:
        engine = get_search_engine()
        
        # Calculate statistics
        recent_queries = engine.performance_stats.get('queries', [])[-100:]
        
        if recent_queries:
            search_times = [q['search_time'] for q in recent_queries]
            avg_time = sum(search_times) / len(search_times)
            min_time = min(search_times)
            max_time = max(search_times)
            
            # Calculate percentiles
            sorted_times = sorted(search_times)
            p50 = sorted_times[len(sorted_times) // 2]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            
            stats = {
                'total_searches': len(recent_queries),
                'average_search_time': round(avg_time, 2),
                'min_search_time': round(min_time, 2),
                'max_search_time': round(max_time, 2),
                'median_search_time': round(p50, 2),
                'p95_search_time': round(p95, 2),
                'cache_enabled': engine.redis_enabled,
                'ml_enabled': engine.sentence_model is not None,
                'recent_queries': [
                    {
                        'query': q['query'],
                        'time': round(q['search_time'], 2),
                        'results': q['results_count']
                    }
                    for q in recent_queries[-10:]
                ]
            }
        else:
            stats = {
                'message': 'No search data available yet'
            }
        
        return jsonify(create_api_response(data=stats))
    
    except Exception as e:
        logger.error(f"Performance stats error: {str(e)}")
        return jsonify(create_error_response(f"Failed to get stats: {str(e)}", 500)), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the search cache (admin endpoint)"""
    try:
        engine = get_search_engine()
        
        if engine.redis_enabled:
            # Clear Redis cache
            keys = engine.redis_client.keys('meditrends:search:*')
            if keys:
                engine.redis_client.delete(*keys)
            message = f"Cleared {len(keys)} cached searches from Redis"
        else:
            # Clear memory cache
            engine.memory_cache.clear()
            message = "Cleared in-memory cache"
        
        logger.info(message)
        
        return jsonify(create_api_response(message=message))
    
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        return jsonify(create_error_response(f"Failed to clear cache: {str(e)}", 500)), 500

# Keep existing endpoints
@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Get search suggestions based on partial query"""
    try:
        partial_query = request.args.get('q', '').strip()
        
        if not partial_query or len(partial_query) < 2:
            return jsonify(create_error_response(
                "Query must be at least 2 characters long",
                400
            )), 400
        
        engine = get_search_engine()
        
        # Get ML-enhanced suggestions
        suggestions = engine._generate_search_suggestions(partial_query)
        
        return jsonify(create_api_response(
            data={'suggestions': suggestions},
            message=f"Found {len(suggestions)} suggestions"
        ))
    
    except Exception as e:
        logger.error(f"Suggestions endpoint error: {str(e)}")
        return jsonify(create_error_response(f"Failed to get suggestions: {str(e)}", 500)), 500

@app.route('/api/subreddits', methods=['GET'])
def get_subreddit_info():
    """Get information about available subreddits"""
    try:
        from subreddit_config import SUBREDDIT_CATEGORIES
        
        category = request.args.get('category', '').strip()
        limit = validate_limit(request.args.get('limit', 100))
        
        if category and category in SUBREDDIT_CATEGORIES:
            category_data = SUBREDDIT_CATEGORIES[category]
            subreddits = category_data['subreddits'][:limit]
            
            result = {
                'category': category,
                'subreddits': subreddits,
                'total_count': len(category_data['subreddits']),
                'priority': category_data['priority'],
                'description': category_data['description']
            }
        else:
            categories_summary = []
            for cat_name, cat_data in SUBREDDIT_CATEGORIES.items():
                categories_summary.append({
                    'name': cat_name,
                    'count': len(cat_data['subreddits']),
                    'priority': cat_data['priority'],
                    'description': cat_data['description'],
                    'sample_subreddits': cat_data['subreddits'][:5]
                })
            
            result = {
                'categories': categories_summary,
                'total_categories': len(SUBREDDIT_CATEGORIES),
                'total_subreddits': sum(len(cat_data['subreddits']) 
                                       for cat_data in SUBREDDIT_CATEGORIES.values())
            }
        
        return jsonify(create_api_response(data=result))
    
    except Exception as e:
        logger.error(f"Subreddits endpoint error: {str(e)}")
        return jsonify(create_error_response(f"Failed to get subreddit info: {str(e)}", 500)), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify(create_error_response("Endpoint not found", 404)), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify(create_error_response("Method not allowed", 405)), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify(create_error_response("Internal server error", 500)), 500

if __name__ == '__main__':
    # Startup message
    print("\n" + "="*60)
    print("🏥 MEDITRENDS ENHANCED BACKEND STARTING 🏥")
    print("="*60)
    print(f"Environment: {config.FLASK_ENV}")
    print(f"Debug Mode: {config.FLASK_DEBUG}")
    print(f"Port: {config.FLASK_PORT}")
    print("\n🚀 New Features:")
    print("  ⚡ Async parallel searches (up to 10x faster)")
    print("  🧠 ML-powered semantic search")
    print("  📈 Trending topics tracking")
    print("  💾 Redis caching support")
    print("  🔄 Streaming search results")
    print("\nAPI Endpoints:")
    print("  📍 GET  /api/health       - Health check")
    print("  🔍 GET  /api/search       - Enhanced search")
    print("  📊 GET  /api/trending     - Trending topics")
    print("  🌊 POST /api/search/stream - Streaming search")
    print("  🧪 POST /api/analyze      - Query analysis")
    print("  📈 GET  /api/performance  - Performance stats")
    print("  💾 POST /api/cache/clear  - Clear cache")
    print("\nExample Usage:")
    print("  curl 'http://localhost:5000/api/search?q=headache+from+computer+screen&use_ml=true'")
    print("="*60)
    
    try:
        app.run(
            host='0.0.0.0',
            port=config.FLASK_PORT,
            debug=config.FLASK_DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 MediTrends Enhanced Backend shutting down...")
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        print(f"\n❌ Failed to start server: {str(e)}")