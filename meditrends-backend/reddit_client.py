"""
Reddit API Client using PRAW
Handles all Reddit API interactions with error handling and rate limiting
"""

import praw
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from config import get_config
from subreddit_config import get_all_subreddits, SUBREDDIT_CATEGORIES

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditClient:
    """Enhanced Reddit client with intelligent search capabilities"""
    
    def __init__(self):
        """Initialize Reddit client with configuration"""
        self.config = get_config()
        self.config.validate_config()
        
        # Initialize PRAW Reddit instance (read-only mode)
        self.reddit = praw.Reddit(
            client_id=self.config.REDDIT_CLIENT_ID,
            client_secret=self.config.REDDIT_CLIENT_SECRET,
            user_agent=self.config.REDDIT_USER_AGENT
        )
        
        # Rate limiting tracking
        self.last_request_time = 0
        self.request_count = 0
        self.start_time = time.time()
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test Reddit API connection"""
        try:
            # Test by accessing a public subreddit (read-only)
            test_sub = self.reddit.subreddit('Health')
            test_title = test_sub.title  # This will trigger an API call
            logger.info(f"Successfully connected to Reddit API (read-only mode)")
            logger.info(f"Test subreddit accessed: r/Health - {test_title}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Reddit API: {str(e)}")
            raise ConnectionError(f"Reddit API connection failed: {str(e)}")
    
    def _rate_limit_check(self):
        """Simple rate limiting to avoid API limits"""
        current_time = time.time()
        time_diff = current_time - self.last_request_time
        
        # Ensure minimum 1 second between requests
        if time_diff < 1:
            sleep_time = 1 - time_diff
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
        
        # Log rate limiting info every 10 requests
        if self.request_count % 10 == 0:
            elapsed = time.time() - self.start_time
            rate = self.request_count / elapsed * 60
            logger.info(f"Request rate: {rate:.1f} requests/minute")
    
    def search_subreddit(self, subreddit_name: str, query: str, 
                        sort: str = 'relevance', time_filter: str = 'all', 
                        limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search a specific subreddit
        
        Args:
            subreddit_name: Name of subreddit to search
            query: Search query string
            sort: Sort method ('relevance', 'hot', 'top', 'new')
            time_filter: Time filter ('all', 'year', 'month', 'week', 'day')
            limit: Maximum number of results
            
        Returns:
            List of post dictionaries
        """
        self._rate_limit_check()
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Perform search based on sort method
            if sort == 'relevance':
                search_results = subreddit.search(query, sort='relevance', 
                                                time_filter=time_filter, limit=limit)
            elif sort == 'top':
                search_results = subreddit.search(query, sort='top', 
                                                time_filter=time_filter, limit=limit)
            elif sort == 'hot':
                search_results = subreddit.search(query, sort='hot', 
                                                time_filter=time_filter, limit=limit)
            elif sort == 'new':
                search_results = subreddit.search(query, sort='new', 
                                                time_filter=time_filter, limit=limit)
            else:
                search_results = subreddit.search(query, limit=limit)
            
            posts = []
            for post in search_results:
                try:
                    post_data = self._extract_post_data(post)
                    if self._is_valid_post(post_data):
                        posts.append(post_data)
                except Exception as e:
                    logger.warning(f"Error processing post {post.id}: {str(e)}")
                    continue
            
            logger.info(f"Found {len(posts)} valid posts in r/{subreddit_name} for query: '{query}'")
            return posts
            
        except Exception as e:
            logger.error(f"Error searching r/{subreddit_name}: {str(e)}")
            return []
    
    def _extract_post_data(self, post) -> Dict[str, Any]:
        """Extract relevant data from a Reddit post"""
        # Get post body text, handle different post types
        body_text = ""
        if hasattr(post, 'selftext') and post.selftext:
            body_text = post.selftext
        elif hasattr(post, 'body') and post.body:
            body_text = post.body
        
        # Create snippet (first 300 characters)
        snippet = body_text[:300] + "..." if len(body_text) > 300 else body_text
        
        # Calculate post age
        post_age = datetime.utcnow() - datetime.utcfromtimestamp(post.created_utc)
        
        return {
            'id': post.id,
            'title': post.title,
            'subreddit': str(post.subreddit),
            'score': post.score,
            'upvote_ratio': getattr(post, 'upvote_ratio', None),
            'num_comments': post.num_comments,
            'body': body_text,
            'snippet': snippet,
            'permalink': f"https://reddit.com{post.permalink}",
            'url': post.url,
            'created_utc': post.created_utc,
            'created_datetime': datetime.utcfromtimestamp(post.created_utc).isoformat(),
            'post_age_days': post_age.days,
            'author': str(post.author) if post.author else '[deleted]',
            'is_self': post.is_self,
            'over_18': post.over_18,
            'spoiler': post.spoiler,
            'stickied': post.stickied
        }
    
    def _is_valid_post(self, post_data: Dict[str, Any]) -> bool:
        """Check if post meets quality criteria"""
        config = self.config
        
        # Check minimum score
        if post_data['score'] < config.MIN_POST_SCORE:
            return False
        
        # Check minimum content length
        if len(post_data['body']) < config.MIN_POST_LENGTH:
            return False
        
        # Check maximum age
        if post_data['post_age_days'] > config.MAX_POST_AGE_DAYS:
            return False
        
        # Skip deleted/removed posts
        if post_data['author'] == '[deleted]':
            return False
        
        # Skip stickied posts (usually announcements)
        if post_data['stickied']:
            return False
        
        return True
    
    def multi_subreddit_search(self, subreddit_list: List[str], query: str,
                              sort: str = 'relevance', time_filter: str = 'all',
                              max_per_subreddit: int = None) -> List[Dict[str, Any]]:
        """
        Search multiple subreddits and combine results
        
        Args:
            subreddit_list: List of subreddit names to search
            query: Search query string
            sort: Sort method for results
            time_filter: Time filter for search
            max_per_subreddit: Maximum results per subreddit
            
        Returns:
            Combined list of posts from all subreddits
        """
        if max_per_subreddit is None:
            max_per_subreddit = self.config.MAX_RESULTS_PER_SUBREDDIT
        
        all_posts = []
        successful_searches = 0
        failed_searches = 0
        
        logger.info(f"Searching {len(subreddit_list)} subreddits for: '{query}'")
        
        for subreddit_name in subreddit_list:
            try:
                posts = self.search_subreddit(
                    subreddit_name=subreddit_name,
                    query=query,
                    sort=sort,
                    time_filter=time_filter,
                    limit=max_per_subreddit
                )
                
                if posts:
                    all_posts.extend(posts)
                    successful_searches += 1
                    logger.debug(f"r/{subreddit_name}: {len(posts)} posts")
                else:
                    failed_searches += 1
                    
            except Exception as e:
                logger.warning(f"Failed to search r/{subreddit_name}: {str(e)}")
                failed_searches += 1
                continue
        
        logger.info(f"Search complete: {successful_searches} successful, {failed_searches} failed")
        logger.info(f"Total posts found: {len(all_posts)}")
        
        return all_posts
    
    def smart_subreddit_selection(self, query: str, max_subreddits: int = 50) -> List[str]:
        """
        Intelligently select subreddits based on query content
        
        Args:
            query: Search query to analyze
            max_subreddits: Maximum number of subreddits to return
            
        Returns:
            List of selected subreddit names
        """
        query_lower = query.lower()
        selected_subreddits = []
        
        # Always include high-priority medical subreddits
        medical_primary = SUBREDDIT_CATEGORIES['medical_primary']['subreddits']
        selected_subreddits.extend(medical_primary[:10])  # Top 10 medical
        
        # Add condition-specific subreddits based on keywords
        keyword_mappings = {
            'pain': ['pain_management', 'chronic_conditions'],
            'headache': ['pain_management'],
            'migraine': ['pain_management'],
            'back': ['pain_management'],
            'neck': ['pain_management'],
            'depression': ['mental_health'],
            'anxiety': ['mental_health'],
            'adhd': ['mental_health'],
            'diabetes': ['chronic_conditions'],
            'thyroid': ['chronic_conditions'],
            'sleep': ['specialized_health'],
            'insomnia': ['specialized_health'],
            'work': ['work_occupational'],
            'job': ['work_occupational'],
            'computer': ['hobby_health_related', 'tech_modern'],
            'gaming': ['hobby_health_related'],
            'exercise': ['lifestyle_wellness'],
            'fitness': ['lifestyle_wellness'],
            'diet': ['lifestyle_wellness'],
            'nutrition': ['lifestyle_wellness'],
            'skin': ['specialized_health'],
            'acne': ['specialized_health'],
            'pregnancy': ['demographics_lifestyle'],
            'pregnant': ['demographics_lifestyle']
        }
        
        # Add relevant category subreddits
        for keyword, categories in keyword_mappings.items():
            if keyword in query_lower:
                for category in categories:
                    if category in SUBREDDIT_CATEGORIES:
                        category_subs = SUBREDDIT_CATEGORIES[category]['subreddits']
                        selected_subreddits.extend(category_subs[:5])  # Top 5 from each relevant category
        
        # Always add some high-volume general subreddits for broader coverage
        general_subs = SUBREDDIT_CATEGORIES['general_large']['subreddits']
        selected_subreddits.extend(general_subs[:8])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_subreddits = []
        for sub in selected_subreddits:
            if sub not in seen:
                seen.add(sub)
                unique_subreddits.append(sub)
        
        # Limit to max_subreddits
        final_subreddits = unique_subreddits[:max_subreddits]
        
        logger.info(f"Selected {len(final_subreddits)} subreddits for query: '{query}'")
        logger.debug(f"Selected subreddits: {final_subreddits[:10]}...")  # Log first 10
        
        return final_subreddits
    
    def get_subreddit_info(self, subreddit_name: str) -> Dict[str, Any]:
        """Get basic information about a subreddit"""
        self._rate_limit_check()
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            return {
                'name': subreddit.display_name,
                'title': subreddit.title,
                'description': subreddit.public_description,
                'subscribers': subreddit.subscribers,
                'active_users': subreddit.active_user_count,
                'over_18': subreddit.over18,
                'created_utc': subreddit.created_utc
            }
        except Exception as e:
            logger.error(f"Error getting info for r/{subreddit_name}: {str(e)}")
            return None
    
    def health_check(self) -> Dict[str, Any]:
        """Check if Reddit API is accessible and working"""
        try:
            # Test basic API functionality (read-only)
            test_sub = self.reddit.subreddit('Health')
            test_sub.title  # This will trigger an API call
            
            return {
                'status': 'healthy',
                'authenticated_user': 'read-only mode',
                'api_accessible': True,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'api_accessible': False,
                'timestamp': datetime.utcnow().isoformat()
            }