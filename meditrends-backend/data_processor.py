"""
Data Processing and NLP utilities for MediTrends
Handles content cleaning, text processing, and basic NLP tasks
"""

import re
import html
import logging
from typing import List, Dict, Any, Set
from datetime import datetime

logger = logging.getLogger(__name__)

class DataProcessor:
    """Data processing and content cleaning utilities"""
    
    def __init__(self):
        """Initialize data processor"""
        # Common Reddit markdown patterns
        self.markdown_patterns = {
            'bold': (r'\*\*(.*?)\*\*', r'\1'),
            'italic': (r'\*(.*?)\*', r'\1'),
            'strikethrough': (r'~~(.*?)~~', r'\1'),
            'code_inline': (r'`(.*?)`', r'\1'),
            'code_block': (r'```[\s\S]*?```', ''),
            'quote': (r'^&gt;\s*(.*)', r'\1'),
            'link': (r'\[([^\]]+)\]\([^)]+\)', r'\1'),
            'subreddit_link': (r'r/(\w+)', r'\1'),
            'user_link': (r'u/(\w+)', r'@\1')
        }
        
        # Medical privacy patterns to remove/anonymize
        self.privacy_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{10,12}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # Dates that might be DOB
        ]
        
        # Common spam/low-quality indicators
        self.spam_indicators = [
            'upvote this', 'please upvote', 'give me karma',
            'click here', 'check out my', 'follow me',
            'buy now', 'limited time', 'act fast',
            'miracle cure', 'doctors hate', 'one weird trick'
        ]
        
        # Medical disclaimers to look for
        self.medical_disclaimers = [
            'not a doctor', 'not medical advice', 'consult your doctor',
            'see a professional', 'seek medical attention', 'go to er',
            'call 911', 'emergency room', 'this is not medical advice'
        ]
        
        logger.info("Data processor initialized")
    
    def process_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a list of posts with cleaning and enhancement
        
        Args:
            posts: List of raw post dictionaries
            
        Returns:
            List of processed and cleaned posts
        """
        processed_posts = []
        
        for post in posts:
            try:
                processed_post = self.process_single_post(post)
                if processed_post and self._is_post_valid(processed_post):
                    processed_posts.append(processed_post)
            except Exception as e:
                logger.warning(f"Error processing post {post.get('id', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Processed {len(processed_posts)} out of {len(posts)} posts")
        return processed_posts
    
    def process_single_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and clean a single post
        
        Args:
            post: Raw post dictionary
            
        Returns:
            Processed post dictionary
        """
        processed_post = post.copy()
        
        # Clean title and body text
        processed_post['title'] = self.clean_text(post['title'])
        processed_post['body'] = self.clean_text(post['body'])
        
        # Create cleaned snippet
        cleaned_body = processed_post['body']
        processed_post['snippet'] = self._create_snippet(cleaned_body, max_length=300)
        
        # Extract and enhance metadata
        processed_post['extracted_info'] = self._extract_post_info(processed_post)
        
        # Add content quality metrics
        processed_post['quality_metrics'] = self._calculate_content_quality(processed_post)
        
        # Add medical relevance indicators
        processed_post['medical_indicators'] = self._detect_medical_content(processed_post)
        
        # Anonymize sensitive information
        processed_post = self._anonymize_sensitive_data(processed_post)
        
        return processed_post
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Decode HTML entities
        cleaned = html.unescape(text)
        
        # Remove Reddit markdown formatting
        for pattern_name, (pattern, replacement) in self.markdown_patterns.items():
            if pattern_name == 'quote':
                # Handle quotes line by line
                lines = cleaned.split('\n')
                cleaned_lines = []
                for line in lines:
                    cleaned_line = re.sub(pattern, replacement, line, flags=re.MULTILINE)
                    cleaned_lines.append(cleaned_line)
                cleaned = '\n'.join(cleaned_lines)
            else:
                cleaned = re.sub(pattern, replacement, cleaned, flags=re.DOTALL)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)  # Multiple newlines to double
        cleaned = re.sub(r' +', ' ', cleaned)  # Multiple spaces to single
        cleaned = cleaned.strip()
        
        # Remove very long URLs (keep short ones as they might be relevant)
        cleaned = re.sub(r'https?://\S{50,}', '[long URL removed]', cleaned)
        
        return cleaned
    
    def _create_snippet(self, text: str, max_length: int = 300) -> str:
        """Create a meaningful snippet from text"""
        if not text:
            return ""
        
        # Try to break at sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        snippet = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(snippet + sentence) <= max_length - 3:
                snippet += sentence + ". "
            else:
                break
        
        snippet = snippet.strip()
        
        # If we couldn't make a good sentence-based snippet, truncate
        if not snippet and text:
            snippet = text[:max_length-3] + "..."
        elif len(snippet) < len(text):
            snippet += "..."
        
        return snippet
    
    def _extract_post_info(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Extract useful information from post content"""
        title = post.get('title', '').lower()
        body = post.get('body', '').lower()
        full_text = f"{title} {body}"
        
        # Extract mentioned medications (basic pattern matching)
        medication_patterns = [
            r'\b\w*(pril|olol|ine|mycin|cillin|zole|ide|ate|pam)\b',  # Common drug endings
            r'\b(tylenol|advil|ibuprofen|acetaminophen|aspirin|aleve)\b',  # OTC meds
            r'\b(adderall|ritalin|lexapro|prozac|zoloft|xanax|ativan)\b'  # Common prescriptions
        ]
        
        medications = set()
        for pattern in medication_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            medications.update(matches)
        
        # Extract symptoms mentioned
        symptom_keywords = [
            'pain', 'headache', 'nausea', 'fatigue', 'dizziness', 'fever',
            'cough', 'shortness of breath', 'chest pain', 'anxiety',
            'depression', 'insomnia', 'swelling', 'rash', 'itching'
        ]
        
        symptoms = [symptom for symptom in symptom_keywords if symptom in full_text]
        
        # Extract age/demographic info
        age_matches = re.findall(r'\b(\d{1,2})[fm]?\b|\b(teen|teenager|elderly|senior)\b', full_text)
        age_info = [match for group in age_matches for match in group if match]
        
        # Extract time indicators
        time_patterns = [
            r'\b(\d+)\s*(day|week|month|year)s?\s*(ago|old)\b',
            r'\b(yesterday|today|recently|lately|for the past)\b'
        ]
        time_indicators = []
        for pattern in time_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            time_indicators.extend([' '.join(match) for match in matches if any(match)])
        
        # Check for question indicators
        is_question = any(word in full_text for word in ['?', 'how', 'what', 'why', 'when', 'help'])
        
        # Check for experience sharing
        shares_experience = any(phrase in full_text for phrase in [
            'i have', 'i had', 'my experience', 'happened to me', 'i went through'
        ])
        
        return {
            'medications_mentioned': list(medications)[:10],  # Limit to avoid clutter
            'symptoms_mentioned': symptoms[:10],
            'age_demographic': age_info[:3],
            'time_indicators': time_indicators[:5],
            'is_question': is_question,
            'shares_experience': shares_experience,
            'word_count': len(full_text.split()),
            'has_medical_disclaimer': any(disclaimer in full_text for disclaimer in self.medical_disclaimers)
        }
    
    def _calculate_content_quality(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate content quality metrics"""
        title = post.get('title', '')
        body = post.get('body', '')
        
        # Length metrics
        title_length = len(title)
        body_length = len(body)
        total_length = title_length + body_length
        
        # Word count
        word_count = len(f"{title} {body}".split())
        
        # Sentence count (rough)
        sentence_count = len(re.findall(r'[.!?]+', f"{title} {body}"))
        
        # Check for spam indicators
        full_text_lower = f"{title} {body}".lower()
        spam_score = sum(1 for indicator in self.spam_indicators if indicator in full_text_lower)
        
        # Calculate readability (simple metric)
        avg_sentence_length = word_count / max(sentence_count, 1)
        readability_score = max(0, min(1, (20 - abs(avg_sentence_length - 15)) / 20))
        
        # Information density (unique words / total words)
        words = f"{title} {body}".lower().split()
        unique_words = len(set(words))
        info_density = unique_words / max(len(words), 1)
        
        return {
            'title_length': title_length,
            'body_length': body_length,
            'total_length': total_length,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'spam_score': spam_score,
            'readability_score': readability_score,
            'information_density': info_density,
            'has_proper_length': 100 <= total_length <= 2000
        }
    
    def _detect_medical_content(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Detect medical content indicators"""
        title = post.get('title', '').lower()
        body = post.get('body', '').lower()
        full_text = f"{title} {body}"
        
        # Medical terminology density
        medical_terms = [
            'symptom', 'diagnosis', 'treatment', 'medication', 'doctor', 'physician',
            'hospital', 'clinic', 'prescription', 'therapy', 'surgery', 'condition',
            'disease', 'disorder', 'syndrome', 'chronic', 'acute', 'patient'
        ]
        
        medical_term_count = sum(1 for term in medical_terms if term in full_text)
        medical_density = medical_term_count / max(len(full_text.split()), 1)
        
        # Urgency indicators
        urgency_terms = [
            'emergency', 'urgent', 'severe', 'acute', 'crisis', 'er', 'hospital',
            'call 911', 'seek immediate', 'go to emergency', 'life threatening'
        ]
        urgency_score = sum(1 for term in urgency_terms if term in full_text)
        
        # Professional advice seeking
        advice_seeking = any(phrase in full_text for phrase in [
            'should i see', 'need to see', 'consult', 'ask doctor', 'medical advice'
        ])
        
        return {
            'medical_term_count': medical_term_count,
            'medical_density': medical_density,
            'urgency_score': urgency_score,
            'seeks_professional_advice': advice_seeking,
            'high_medical_relevance': medical_density > 0.05 or medical_term_count > 3
        }
    
    def _anonymize_sensitive_data(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or anonymize sensitive personal information"""
        processed_post = post.copy()
        
        # Anonymize text fields
        for field in ['title', 'body', 'snippet']:
            if field in processed_post:
                text = processed_post[field]
                
                # Remove patterns that look like sensitive data
                for pattern in self.privacy_patterns:
                    text = re.sub(pattern, '[REDACTED]', text)
                
                # Remove specific personal identifiers
                text = re.sub(r'\bmy name is \w+\b', 'my name is [NAME]', text, flags=re.IGNORECASE)
                text = re.sub(r'\bi live in [\w\s]+\b', 'I live in [LOCATION]', text, flags=re.IGNORECASE)
                
                processed_post[field] = text
        
        return processed_post
    
    def _is_post_valid(self, post: Dict[str, Any]) -> bool:
        """Check if processed post meets quality standards"""
        quality_metrics = post.get('quality_metrics', {})
        
        # Check minimum quality requirements
        if quality_metrics.get('spam_score', 0) > 2:
            return False
        
        if quality_metrics.get('total_length', 0) < 20:
            return False
        
        if quality_metrics.get('word_count', 0) < 5:
            return False
        
        # Check for deleted/removed content
        if post.get('body', '').lower() in ['[deleted]', '[removed]', '']:
            return False
        
        return True
    
    def extract_health_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract health-related entities from text (basic NLP)"""
        text_lower = text.lower()
        
        # Body parts
        body_parts = [
            'head', 'brain', 'eye', 'ear', 'nose', 'throat', 'neck', 'shoulder',
            'arm', 'hand', 'finger', 'chest', 'heart', 'lung', 'back', 'spine',
            'abdomen', 'stomach', 'liver', 'kidney', 'hip', 'leg', 'knee', 'foot'
        ]
        found_body_parts = [part for part in body_parts if part in text_lower]
        
        # Symptoms
        symptoms = [
            'pain', 'ache', 'headache', 'migraine', 'nausea', 'vomiting', 'fever',
            'fatigue', 'tired', 'dizzy', 'weakness', 'numbness', 'tingling',
            'swelling', 'inflammation', 'rash', 'itching', 'burning', 'stinging'
        ]
        found_symptoms = [symptom for symptom in symptoms if symptom in text_lower]
        
        # Conditions (basic)
        conditions = [
            'diabetes', 'hypertension', 'depression', 'anxiety', 'arthritis',
            'asthma', 'allergy', 'infection', 'cancer', 'tumor', 'cyst'
        ]
        found_conditions = [condition for condition in conditions if condition in text_lower]
        
        return {
            'body_parts': found_body_parts,
            'symptoms': found_symptoms,
            'conditions': found_conditions
        }
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity using word overlap"""
        if not text1 or not text2:
            return 0.0
        
        # Tokenize and clean
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def get_content_stats(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about processed content"""
        if not posts:
            return {'total_posts': 0}
        
        total_posts = len(posts)
        total_words = sum(post.get('quality_metrics', {}).get('word_count', 0) for post in posts)
        avg_word_count = total_words / total_posts
        
        # Count posts with medical content
        medical_posts = sum(1 for post in posts 
                          if post.get('medical_indicators', {}).get('high_medical_relevance', False))
        
        # Count questions vs experiences
        questions = sum(1 for post in posts 
                       if post.get('extracted_info', {}).get('is_question', False))
        experiences = sum(1 for post in posts 
                         if post.get('extracted_info', {}).get('shares_experience', False))
        
        return {
            'total_posts': total_posts,
            'total_words': total_words,
            'average_word_count': avg_word_count,
            'medical_relevant_posts': medical_posts,
            'medical_relevance_percentage': (medical_posts / total_posts * 100) if total_posts > 0 else 0,
            'question_posts': questions,
            'experience_posts': experiences,
            'question_percentage': (questions / total_posts * 100) if total_posts > 0 else 0
        }