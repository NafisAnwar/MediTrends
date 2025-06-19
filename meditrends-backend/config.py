"""
Configuration settings for MediTrends Backend
"""

import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""

    # ─── Flask ────────────────────────────────────────────────────────────────
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

    # ─── Reddit API Configuration ────────────────────────────────────────────
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'MediTrends/1.0')

    # ─── Search Limits ─────────────────────────────────────────────────────────
    MAX_RESULTS_PER_SUBREDDIT = int(os.getenv('MAX_RESULTS_PER_SUBREDDIT', 20))
    TOTAL_MAX_RESULTS = int(os.getenv('TOTAL_MAX_RESULTS', 100))
    SEARCH_TIME_LIMIT = int(os.getenv('SEARCH_TIME_LIMIT', 30))  # seconds

    # ─── Redis Cache ──────────────────────────────────────────────────────────
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    # You can override with a full URL if desired
    REDIS_URL = os.getenv(
        'REDIS_URL',
        f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    )

    # ─── ML / NLP Settings ────────────────────────────────────────────────────
    # HuggingFace model name for automatic download & caching
    SENTENCE_TRANSFORMER_MODEL = os.getenv(
        'SENTENCE_TRANSFORMER_MODEL',
        'all-MiniLM-L6-v2'
    )

    # ─── Thread Pool ──────────────────────────────────────────────────────────
    NUM_THREADS = int(os.getenv('NUM_THREADS', 8))

    # ─── Post Quality Thresholds ─────────────────────────────────────────────
    # (so reddit_client._is_valid_post has something to read)
    MIN_POST_SCORE    = int(os.getenv('MIN_POST_SCORE',    0))
    MIN_POST_LENGTH   = int(os.getenv('MIN_POST_LENGTH',   30))
    MAX_POST_AGE_DAYS = int(os.getenv('MAX_POST_AGE_DAYS', 365))

    def validate_config(self):
        """
        Ensure that all required config values are present.
        Called at startup and before initializing PRAW.
        """
        missing = []
        for var in ('REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT'):
            if not getattr(self, var):
                missing.append(var)
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

    @property
    def sentence_model(self) -> SentenceTransformer:
        """
        Lazy-load the SentenceTransformer model on first access.
        Downloads & caches weights automatically in ~/.cache.
        """
        if not hasattr(self, '_sentence_model'):
            self._sentence_model = SentenceTransformer(self.SENTENCE_TRANSFORMER_MODEL)
        return self._sentence_model


class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing-specific configuration"""
    TESTING = True
    DEBUG = True


# ─── Configuration Mapping & Loader ────────────────────────────────────────
_config_mapping = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     DevelopmentConfig
}


def get_config() -> Config:
    """
    Return an *instance* of the config class matching FLASK_ENV.
    """
    env = os.getenv('FLASK_ENV', 'development')
    config_cls = _config_mapping.get(env, _config_mapping['default'])
    return config_cls()
