"""
Enhanced Search Engine for MediTrends with Async, ML, and Advanced Features
Dramatically improves speed and relevance using modern techniques
"""

import asyncio
import aiohttp
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import math
import re
import logging
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json

# ML/NLP imports
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# For Redis caching
import redis
import pickle

# Import existing modules
from reddit_client import RedditClient
from data_processor import DataProcessor
from subreddit_config import get_medical_terms, SUBREDDIT_CATEGORIES
from config import get_config

logger = logging.getLogger(__name__)

class EnhancedSearchEngine:
    """Next-generation search engine with ML, async, and advanced features"""
    
    def __init__(self):
        """Initialize enhanced search engine components"""
        self.config = get_config()
        self.reddit_client = RedditClient()
        self.data_processor = DataProcessor()
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.Redis(
                host='localhost', 
                port=6379, 
                decode_responses=False,
                connection_pool_timeout=20
            )
            self.redis_client.ping()
            self.redis_enabled = True
            logger.info("Redis cache initialized successfully")
        except:
            self.redis_enabled = False
            logger.warning("Redis not available, falling back to in-memory cache")
            self.memory_cache = {}
        
        # Initialize ML models
        self._initialize_ml_models()
        
        # Initialize async components
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Query performance tracking
        self.performance_stats = defaultdict(list)
        
        # Trending topics tracker
        self.trending_tracker = TrendingTopicsTracker()
        
        logger.info("Enhanced search engine initialized successfully")
    
    def _initialize_ml_models(self):
        """Initialize ML/NLP models for better search"""
        try:
            # Sentence transformer for semantic similarity
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer loaded")
            
            # SpaCy for medical NER
            try:
                self.nlp = spacy.load("en_core_sci_md")  # Scientific/medical model
            except:
                self.nlp = spacy.load("en_core_web_sm")  # Fallback to general model
            logger.info("SpaCy model loaded")
            
            # TF-IDF vectorizer for keyword importance
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 3),
                stop_words='english'
            )
            
            # Download NLTK data
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error loading ML models: {str(e)}")
            self.sentence_model = None
            self.nlp = None
    
    async def search_async(self, query: str, sort: str = 'relevance', 
                          time_filter: str = 'all', limit: int = None,
                          use_ml: bool = True) -> Dict[str, Any]:
        """
        Async search with ML enhancements - LIGHTNING FAST VERSION
        """
        if limit is None:
            limit = self.config.TOTAL_MAX_RESULTS
        
        start_time = datetime.utcnow()
        logger.info(f"Starting ASYNC search for: '{query}'")
        
        try:
            # Step 1: Quick cache check with Redis
            cache_key = self._generate_cache_key(query, sort, time_filter, limit)
            cached_result = await self._get_from_cache_async(cache_key)
            if cached_result:
                logger.info("Returning cached results (instant)")
                return cached_result
            
            # Step 2: Advanced query analysis with ML
            analyzed_query = await self._analyze_query_ml(query) if use_ml else self._analyze_query(query)
            
            # Step 3: Smart subreddit selection with ML ranking
            selected_subreddits = await self._smart_subreddit_selection_ml(
                query, analyzed_query
            ) if use_ml else self.reddit_client.smart_subreddit_selection(query, max_subreddits=20)
            
            # Step 4: PARALLEL async Reddit searches (HUGE SPEED IMPROVEMENT)
            search_tasks = []
            for subreddit in selected_subreddits[:15]:  # Limit for speed
                task = self._search_subreddit_async(
                    subreddit, query, sort, time_filter, 
                    limit=10  # Reduced per-subreddit limit
                )
                search_tasks.append(task)
            
            # Execute all searches in parallel
            all_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Combine results
            raw_posts = []
            for result in all_results:
                if isinstance(result, list):
                    raw_posts.extend(result)
            
            if not raw_posts:
                return self._create_empty_result(query, "No posts found")
            
            # Step 5: Quick quality filter
            filtered_posts = self._quick_quality_filter(raw_posts)
            
            # Step 6: Process posts with NLP enhancements
            processed_posts = await self._process_posts_async(filtered_posts)
            
            # Step 7: Advanced ML scoring if enabled
            if use_ml and self.sentence_model:
                scored_posts = await self._score_posts_ml(processed_posts, query, analyzed_query)
            else:
                scored_posts = self._score_posts(processed_posts, analyzed_query)
            
            # Step 8: Smart deduplication with fuzzy matching
            deduplicated_posts = self._smart_deduplicate(scored_posts)
            
            # Step 9: Final ranking with diversity
            final_results = self._diverse_ranking(deduplicated_posts, limit)
            
            # Step 10: Track trending topics
            self.trending_tracker.update(query, final_results)
            
            # Create response
            search_time = (datetime.utcnow() - start_time).total_seconds()
            result = self._create_enhanced_search_result(
                query=query,
                posts=final_results,
                total_found=len(raw_posts),
                total_processed=len(processed_posts),
                total_returned=len(final_results),
                search_time=search_time,
                subreddits_searched=selected_subreddits,
                analyzed_query=analyzed_query,
                ml_used=use_ml,
                trending_topics=self.trending_tracker.get_trending()
            )
            
            # Cache result
            await self._add_to_cache_async(cache_key, result)
            
            # Track performance
            self._track_performance(query, search_time, len(final_results))
            
            logger.info(f"ASYNC search completed in {search_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Async search failed: {str(e)}")
            return self._create_error_result(query, str(e))
    
    async def _analyze_query_ml(self, query: str) -> Dict[str, Any]:
        """Analyze query using ML/NLP techniques"""
        base_analysis = self._analyze_query(query)
        
        if not self.nlp:
            return base_analysis
        
        # NLP analysis
        doc = self.nlp(query)
        
        # Extract entities
        entities = {
            'medical_conditions': [],
            'medications': [],
            'symptoms': [],
            'body_parts': [],
            'treatments': []
        }
        
        for ent in doc.ents:
            if ent.label_ in ['DISEASE', 'CONDITION']:
                entities['medical_conditions'].append(ent.text.lower())
            elif ent.label_ in ['DRUG', 'MEDICATION']:
                entities['medications'].append(ent.text.lower())
            elif ent.label_ in ['SYMPTOM']:
                entities['symptoms'].append(ent.text.lower())
            elif ent.label_ in ['BODY_PART', 'ANATOMY']:
                entities['body_parts'].append(ent.text.lower())
            elif ent.label_ in ['TREATMENT', 'PROCEDURE']:
                entities['treatments'].append(ent.text.lower())
        
        # Semantic query expansion
        query_embedding = None
        if self.sentence_model:
            query_embedding = self.sentence_model.encode(query)
        
        base_analysis.update({
            'entities': entities,
            'query_embedding': query_embedding,
            'pos_tags': [(token.text, token.pos_) for token in doc],
            'key_phrases': [chunk.text for chunk in doc.noun_chunks]
        })
        
        return base_analysis
    
    async def _smart_subreddit_selection_ml(self, query: str, analyzed_query: Dict) -> List[str]:
        """ML-enhanced subreddit selection"""
        # Start with basic selection
        base_subreddits = self.reddit_client.smart_subreddit_selection(query, max_subreddits=30)
        
        if not self.sentence_model or not analyzed_query.get('query_embedding') is not None:
            return base_subreddits[:20]
        
        # Score subreddits based on semantic similarity to query
        subreddit_scores = []
        
        for subreddit in base_subreddits:
            # Get subreddit description/category
            category_desc = self._get_subreddit_description(subreddit)
            if category_desc:
                # Calculate semantic similarity
                desc_embedding = self.sentence_model.encode(category_desc)
                similarity = cosine_similarity(
                    [analyzed_query['query_embedding']], 
                    [desc_embedding]
                )[0][0]
                subreddit_scores.append((subreddit, similarity))
            else:
                subreddit_scores.append((subreddit, 0.5))  # Default score
        
        # Sort by similarity score
        subreddit_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top subreddits
        return [sub[0] for sub in subreddit_scores[:20]]
    
    async def _search_subreddit_async(self, subreddit: str, query: str, 
                                    sort: str, time_filter: str, limit: int) -> List[Dict]:
        """Async wrapper for subreddit search"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.reddit_client.search_subreddit,
            subreddit, query, sort, time_filter, limit
        )
    
    async def _process_posts_async(self, posts: List[Dict]) -> List[Dict]:
        """Async post processing"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.data_processor.process_posts,
            posts
        )
    
    async def _score_posts_ml(self, posts: List[Dict], query: str, analyzed_query: Dict) -> List[Dict]:
        """Score posts using ML techniques"""
        scored_posts = []
        
        # Get query embedding
        if not self.sentence_model or analyzed_query.get('query_embedding') is None:
            return self._score_posts(posts, analyzed_query)
        
        query_embedding = analyzed_query['query_embedding']
        
        # Prepare post texts for batch encoding
        post_texts = [f"{p['title']} {p['body'][:500]}" for p in posts]
        
        # Batch encode all posts
        post_embeddings = self.sentence_model.encode(post_texts, batch_size=32)
        
        for i, post in enumerate(posts):
            # Calculate semantic similarity
            semantic_score = cosine_similarity(
                [query_embedding], 
                [post_embeddings[i]]
            )[0][0]
            
            # Get traditional relevance score
            traditional_score = self._calculate_relevance_score(post, analyzed_query)
            
            # Combine scores (60% semantic, 40% traditional)
            final_score = (semantic_score * 0.6) + (traditional_score * 0.4)
            
            # Add entity matching bonus
            entity_score = self._calculate_entity_match_score(post, analyzed_query.get('entities', {}))
            final_score += entity_score * 0.1
            
            post['relevance_score'] = min(final_score, 1.0)
            post['semantic_score'] = semantic_score
            post['traditional_score'] = traditional_score
            scored_posts.append(post)
        
        return scored_posts
    
    def _calculate_entity_match_score(self, post: Dict, entities: Dict) -> float:
        """Calculate score based on entity matches"""
        if not entities:
            return 0.0
        
        text = f"{post['title']} {post['body']}".lower()
        total_entities = sum(len(v) for v in entities.values())
        
        if total_entities == 0:
            return 0.0
        
        matches = 0
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                if entity in text:
                    matches += 1
        
        return matches / total_entities
    
    def _smart_deduplicate(self, posts: List[Dict]) -> List[Dict]:
        """Smart deduplication using fuzzy matching and semantic similarity"""
        if not posts:
            return posts
        
        deduplicated = []
        seen_hashes = set()
        seen_titles = []
        
        for post in sorted(posts, key=lambda x: x.get('relevance_score', 0), reverse=True):
            # Create content hash
            content_hash = hashlib.md5(
                f"{post['title']}_{post['subreddit']}".encode()
            ).hexdigest()
            
            if content_hash in seen_hashes:
                continue
            
            # Check fuzzy title similarity
            is_duplicate = False
            post_title_lower = post['title'].lower()
            
            for seen_title in seen_titles:
                similarity = self._calculate_title_similarity(post_title_lower, seen_title)
                if similarity > 0.85:  # 85% similarity threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_hashes.add(content_hash)
                seen_titles.append(post_title_lower)
                deduplicated.append(post)
        
        return deduplicated
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate title similarity using multiple methods"""
        # Jaccard similarity
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        jaccard = intersection / union if union > 0 else 0
        
        # Levenshtein distance (normalized)
        max_len = max(len(title1), len(title2))
        if max_len == 0:
            return 1.0
        
        distance = self._levenshtein_distance(title1, title2)
        normalized_distance = 1 - (distance / max_len)
        
        # Combined score
        return (jaccard * 0.7) + (normalized_distance * 0.3)
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _diverse_ranking(self, posts: List[Dict], limit: int) -> List[Dict]:
        """Rank results with diversity to avoid same-subreddit clustering"""
        if not posts:
            return posts
        
        # Sort by relevance
        sorted_posts = sorted(posts, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Implement MMR (Maximal Marginal Relevance) for diversity
        selected = []
        remaining = sorted_posts.copy()
        subreddit_counts = defaultdict(int)
        
        while len(selected) < limit and remaining:
            best_score = -1
            best_post = None
            best_idx = -1
            
            for i, post in enumerate(remaining):
                # Calculate MMR score
                relevance = post.get('relevance_score', 0)
                
                # Penalty for subreddit over-representation
                subreddit = post.get('subreddit', '')
                diversity_penalty = min(subreddit_counts[subreddit] * 0.1, 0.3)
                
                mmr_score = relevance - diversity_penalty
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_post = post
                    best_idx = i
            
            if best_post:
                selected.append(best_post)
                subreddit_counts[best_post.get('subreddit', '')] += 1
                remaining.pop(best_idx)
        
        return selected
    
    async def _get_from_cache_async(self, cache_key: str) -> Optional[Dict]:
        """Get from Redis cache asynchronously"""
        if not self.redis_enabled:
            return self.memory_cache.get(cache_key)
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return pickle.loads(cached_data)
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
        
        return None
    
    async def _add_to_cache_async(self, cache_key: str, data: Dict, ttl_seconds: int = 1800):
        """Add to Redis cache asynchronously"""
        if not self.redis_enabled:
            self.memory_cache[cache_key] = data
            return
        
        try:
            serialized_data = pickle.dumps(data)
            self.redis_client.setex(cache_key, ttl_seconds, serialized_data)
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
    
    def _generate_cache_key(self, query: str, sort: str, time_filter: str, limit: int) -> str:
        """Generate cache key"""
        key_data = f"{query.lower().strip()}_{sort}_{time_filter}_{limit}"
        return f"meditrends:search:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _get_subreddit_description(self, subreddit: str) -> Optional[str]:
        """Get subreddit description for semantic matching"""
        for category, data in SUBREDDIT_CATEGORIES.items():
            if subreddit in data['subreddits']:
                return data['description']
        return None
    
    def _track_performance(self, query: str, search_time: float, results_count: int):
        """Track search performance for analytics"""
        self.performance_stats['queries'].append({
            'query': query,
            'timestamp': datetime.utcnow(),
            'search_time': search_time,
            'results_count': results_count
        })
        
        # Keep only last 1000 queries
        if len(self.performance_stats['queries']) > 1000:
            self.performance_stats['queries'] = self.performance_stats['queries'][-1000:]
    
    def _create_enhanced_search_result(self, **kwargs) -> Dict[str, Any]:
        """Create enhanced search result with ML metadata"""
        base_result = self._create_search_result(**kwargs)
        
        # Add ML-specific metadata
        base_result['metadata'].update({
            'ml_used': kwargs.get('ml_used', False),
            'trending_topics': kwargs.get('trending_topics', []),
            'search_suggestions': self._generate_search_suggestions(kwargs['query']),
            'related_queries': self._get_related_queries(kwargs['query'])
        })
        
        return base_result
    
    def _generate_search_suggestions(self, query: str) -> List[str]:
        """Generate intelligent search suggestions"""
        suggestions = []
        query_lower = query.lower()
        
        # Add medical context suggestions
        medical_contexts = [
            f"{query} causes",
            f"{query} symptoms",
            f"{query} treatment",
            f"{query} side effects",
            f"{query} natural remedies",
            f"{query} prevention"
        ]
        
        suggestions.extend(medical_contexts[:3])
        
        # Add trending related terms
        trending = self.trending_tracker.get_related_trending(query)
        suggestions.extend(trending[:2])
        
        return suggestions[:5]
    
    def _get_related_queries(self, query: str) -> List[str]:
        """Get related queries based on search history"""
        # Simple implementation - in production, this would use collaborative filtering
        related = []
        
        # Check recent queries for similarity
        recent_queries = [q['query'] for q in self.performance_stats['queries'][-50:]]
        query_words = set(query.lower().split())
        
        for recent_query in recent_queries:
            if recent_query.lower() != query.lower():
                recent_words = set(recent_query.lower().split())
                overlap = len(query_words.intersection(recent_words))
                if overlap >= 1:
                    related.append(recent_query)
        
        return list(set(related))[:3]
    
    # Keep all existing methods from original SearchEngine class
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Original query analysis method"""
        # Implementation from original file
        query_lower = query.lower()
        
        # Extract medical terms
        medical_terms = get_medical_terms()
        found_medical_terms = [term for term in medical_terms if term in query_lower]
        
        # Intent detection
        question_words = ['how', 'what', 'why', 'when', 'where', 'who', 'which', 'can', 'should', 'is', 'does']
        has_question = any(word in query_lower for word in question_words) or '?' in query
        
        # Temporal indicators
        temporal_indicators = ['today', 'yesterday', 'recent', 'lately', 'now', 'current', 'new', 'sudden']
        is_time_sensitive = any(indicator in query_lower for indicator in temporal_indicators)
        
        # Experience indicators
        experience_indicators = ['anyone else', 'has anyone', 'similar experience', 'same problem', 'me too', 'also have']
        seeks_experiences = any(indicator in query_lower for indicator in experience_indicators)
        
        # Cause indicators
        cause_indicators = ['from', 'after', 'caused by', 'due to', 'because of', 'why do i', 'what causes']
        seeks_cause = any(indicator in query_lower for indicator in cause_indicators)
        
        # Solution indicators
        solution_indicators = ['how to', 'treatment', 'cure', 'fix', 'help', 'relief', 'stop', 'prevent']
        seeks_solution = any(indicator in query_lower for indicator in solution_indicators)
        
        return {
            'original_query': query,
            'cleaned_query': query_lower,
            'medical_terms': found_medical_terms,
            'has_question': has_question,
            'is_time_sensitive': is_time_sensitive,
            'seeks_experiences': seeks_experiences,
            'seeks_cause': seeks_cause,
            'seeks_solution': seeks_solution,
            'query_length': len(query.split()),
            'complexity_score': self._calculate_query_complexity(query),
            'primary_intent': self._determine_primary_intent(query_lower, seeks_cause, seeks_solution, seeks_experiences, has_question)
        }
    
    def _calculate_query_complexity(self, query: str) -> float:
        """Calculate query complexity score"""
        words = query.lower().split()
        word_count_score = min(len(words) / 10, 1.0)
        
        medical_terms = get_medical_terms()
        medical_term_count = sum(1 for word in words if word in medical_terms)
        medical_score = min(medical_term_count / 3, 1.0)
        
        return min((word_count_score + medical_score) / 2, 1.0)
    
    def _determine_primary_intent(self, query_lower: str, seeks_cause: bool, seeks_solution: bool, seeks_experiences: bool, has_question: bool) -> str:
        """Determine primary intent"""
        if seeks_cause:
            return 'cause_seeking'
        elif seeks_solution:
            return 'solution_seeking'
        elif seeks_experiences:
            return 'experience_sharing'
        elif has_question:
            return 'information_seeking'
        else:
            return 'general_search'
    
    def _score_posts(self, posts: List[Dict], analyzed_query: Dict) -> List[Dict]:
        """Original scoring method"""
        scored_posts = []
        for post in posts:
            relevance_score = self._calculate_relevance_score(post, analyzed_query)
            post['relevance_score'] = relevance_score
            scored_posts.append(post)
        return scored_posts
    
    def _calculate_relevance_score(self, post: Dict, analyzed_query: Dict) -> float:
        """Original relevance calculation"""
        score = 0.0
        full_text = f"{post['title']} {post['body']}".lower()
        query_lower = analyzed_query['cleaned_query']
        
        # Keyword matching (50%)
        keyword_score = self._calculate_keyword_score(full_text, query_lower)
        score += keyword_score * 0.5
        
        # Medical term matching (25%)
        medical_score = self._calculate_medical_term_score(full_text, analyzed_query['medical_terms'])
        score += medical_score * 0.25
        
        # Quality score (15%)
        quality_score = self._calculate_quality_score(post)
        score += quality_score * 0.15
        
        # Recency score (10%)
        recency_score = self._calculate_recency_score(post, analyzed_query['is_time_sensitive'])
        score += recency_score * 0.1
        
        return min(score, 1.0)
    
    def _calculate_keyword_score(self, text: str, query: str) -> float:
        """Calculate keyword score"""
        query_words = set(query.split())
        text_words = set(text.split())
        
        if not query_words:
            return 0
        
        exact_matches = len(query_words.intersection(text_words))
        exact_score = exact_matches / len(query_words)
        phrase_bonus = 0.3 if query in text else 0
        
        return min(exact_score + phrase_bonus, 1.0)
    
    def _calculate_medical_term_score(self, text: str, medical_terms: List[str]) -> float:
        """Calculate medical term score"""
        if not medical_terms:
            return 0.0
        
        found_terms = [term for term in medical_terms if term in text]
        return len(found_terms) / len(medical_terms)
    
    def _calculate_quality_score(self, post: Dict) -> float:
        """Calculate post quality score"""
        quality_score = 0.0
        
        if post.get('score', 0) > 0:
            upvote_score = min(math.log10(post.get('score', 0) + 1) / 3, 0.4)
            quality_score += upvote_score
        
        if post.get('num_comments', 0) > 0:
            comment_score = min(math.log10(post.get('num_comments', 0) + 1) / 2, 0.3)
            quality_score += comment_score
        
        content_length = len(post.get('body', ''))
        if 200 <= content_length <= 800:
            length_score = 0.2
        elif 100 <= content_length < 200:
            length_score = 0.1
        else:
            length_score = 0.0
        
        quality_score += length_score
        
        return min(quality_score, 1.0)
    
    def _calculate_recency_score(self, post: Dict, is_time_sensitive: bool) -> float:
        """Calculate recency score"""
        days_old = post.get('post_age_days', 365)
        
        if not is_time_sensitive:
            if days_old <= 30:
                return 0.3
            elif days_old <= 90:
                return 0.2
            elif days_old <= 365:
                return 0.1
            else:
                return 0.0
        else:
            if days_old <= 7:
                return 1.0
            elif days_old <= 30:
                return 0.7
            elif days_old <= 90:
                return 0.4
            else:
                return 0.0
    
    def _quick_quality_filter(self, posts: List[Dict]) -> List[Dict]:
        """Quick quality filter"""
        filtered_posts = []
        
        for post in posts:
            if (post.get('score', 0) < -10 or
                len(post.get('body', '')) < 30 or
                post.get('author') == '[deleted]' or
                '[removed]' in post.get('body', '').lower()):
                continue
            
            filtered_posts.append(post)
        
        logger.info(f"Quick filter: {len(posts)} -> {len(filtered_posts)} posts")
        return filtered_posts
    
    def _create_search_result(self, **kwargs) -> Dict[str, Any]:
        """Create formatted search result"""
        return {
            'query': kwargs['query'],
            'results': kwargs['posts'],
            'metadata': {
                'total_found': kwargs['total_found'],
                'total_processed': kwargs['total_processed'],
                'total_returned': kwargs['total_returned'],
                'search_time_seconds': kwargs['search_time'],
                'subreddits_searched': len(kwargs['subreddits_searched']),
                'timestamp': datetime.utcnow().isoformat(),
                'query_analysis': kwargs['analyzed_query'],
                'performance_grade': self._calculate_performance_grade(kwargs['search_time'])
            },
            'status': 'success'
        }
    
    def _calculate_performance_grade(self, search_time: float) -> str:
        """Calculate performance grade"""
        if search_time < 5:
            return 'A+ (Excellent)'
        elif search_time < 10:
            return 'A (Very Good)'
        elif search_time < 20:
            return 'B (Good)'
        elif search_time < 30:
            return 'C (Acceptable)'
        else:
            return 'D (Needs Improvement)'
    
    def _create_empty_result(self, query: str, message: str) -> Dict[str, Any]:
        """Create empty result"""
        return {
            'query': query,
            'results': [],
            'metadata': {
                'total_found': 0,
                'total_processed': 0,
                'total_returned': 0,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            },
            'status': 'success'
        }
    
    def _create_error_result(self, query: str, error: str) -> Dict[str, Any]:
        """Create error result"""
        return {
            'query': query,
            'results': [],
            'metadata': {
                'error': error,
                'timestamp': datetime.utcnow().isoformat()
            },
            'status': 'error'
        }


class TrendingTopicsTracker:
    """Track trending health topics and queries"""
    
    def __init__(self, window_hours: int = 24):
        self.window_hours = window_hours
        self.query_history = defaultdict(list)
        self.topic_scores = defaultdict(float)
        
    def update(self, query: str, results: List[Dict]):
        """Update trending based on query and results"""
        current_time = datetime.utcnow()
        
        # Track query
        self.query_history[query.lower()].append(current_time)
        
        # Extract topics from results
        for post in results[:10]:  # Top 10 results
            # Extract key terms from title
            title_words = post['title'].lower().split()
            for word in title_words:
                if len(word) > 3 and word not in stopwords.words('english'):
                    self.topic_scores[word] += post.get('relevance_score', 0.5)
        
        # Clean old entries
        self._clean_old_entries()
    
    def get_trending(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get current trending topics"""
        current_time = datetime.utcnow()
        trending = []
        
        # Calculate scores with time decay
        for topic, base_score in self.topic_scores.items():
            # Apply time decay
            topic_queries = []
            for query, times in self.query_history.items():
                if topic in query:
                    topic_queries.extend(times)
            
            if topic_queries:
                # Calculate recency boost
                latest_time = max(topic_queries)
                hours_ago = (current_time - latest_time).total_seconds() / 3600
                time_decay = math.exp(-hours_ago / 12)  # 12-hour half-life
                
                final_score = base_score * time_decay * len(topic_queries)
                
                trending.append({
                    'topic': topic,
                    'score': final_score,
                    'query_count': len(topic_queries),
                    'last_seen': latest_time.isoformat()
                })
        
        # Sort by score
        trending.sort(key=lambda x: x['score'], reverse=True)
        
        return trending[:limit]
    
    def get_related_trending(self, query: str) -> List[str]:
        """Get trending topics related to a query"""
        query_words = set(query.lower().split())
        related = []
        
        for topic_data in self.get_trending(20):
            topic = topic_data['topic']
            if topic in query_words or any(word in topic for word in query_words):
                related.append(topic)
        
        return related[:5]
    
    def _clean_old_entries(self):
        """Remove entries older than window"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.window_hours)
        
        # Clean query history
        for query in list(self.query_history.keys()):
            self.query_history[query] = [
                t for t in self.query_history[query] if t > cutoff_time
            ]
            if not self.query_history[query]:
                del self.query_history[query]
        
        # Decay topic scores
        decay_factor = 0.95
        for topic in list(self.topic_scores.keys()):
            self.topic_scores[topic] *= decay_factor
            if self.topic_scores[topic] < 0.1:
                del self.topic_scores[topic]