"""
Configuration management for the JanusGraph ScyllaDB example application.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
# Get the project root directory (3 levels up from this file)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_file_path = os.path.join(project_root, '.env')
load_dotenv(env_file_path)


class DatabaseConfig(BaseSettings):
    """Database connection configuration for both JanusGraph and ScyllaDB."""
    
    # ScyllaDB/Cassandra connection settings
    host: str = Field(default_factory=lambda: os.environ.get('SCYLLA_HOST', 'localhost'))
    port: int = Field(default_factory=lambda: int(os.environ.get('SCYLLA_PORT', '9042')))
    username: Optional[str] = Field(default_factory=lambda: os.environ.get('SCYLLA_USERNAME'))
    password: Optional[str] = Field(default_factory=lambda: os.environ.get('SCYLLA_PASSWORD'))
    
    # Keyspace settings
    janusgraph_keyspace: str = Field(default_factory=lambda: os.environ.get('SCYLLA_KEYSPACE', 'janusgraph'))
    ecommerce_keyspace: str = Field(default_factory=lambda: os.environ.get('ECOMMERCE_KEYSPACE', 'ecommerce'))
    
    # SSL settings
    ssl_enabled: bool = Field(default_factory=lambda: os.environ.get('SCYLLA_SSL_ENABLED', 'false').lower() == 'true')
    ssl_cert_path: Optional[str] = Field(default_factory=lambda: os.environ.get('SCYLLA_SSL_CERT_PATH'))
    
    # Connection pool settings
    connection_timeout: int = Field(default_factory=lambda: int(os.environ.get('CONNECTION_TIMEOUT', '10')))
    request_timeout: int = Field(default_factory=lambda: int(os.environ.get('REQUEST_TIMEOUT', '30')))
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore", "env_nested_delimiter": "__"}


class JanusGraphConfig(BaseSettings):
    """JanusGraph-specific configuration."""
    
    # Gremlin server connection
    gremlin_host: str = Field(default="localhost", env="JANUSGRAPH_HOST")
    gremlin_port: int = Field(default=8182, env="JANUSGRAPH_PORT")
    
    # Traversal settings
    max_workers: int = Field(default=4, env="GREMLIN_MAX_WORKERS")
    
    @property
    def gremlin_url(self) -> str:
        """Get the Gremlin server WebSocket URL."""
        return f"ws://{self.gremlin_host}:{self.gremlin_port}/gremlin"
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


class ApplicationConfig(BaseSettings):
    """Application-level configuration."""
    
    # Data generation settings
    num_users: int = Field(default=100, env="NUM_USERS")
    num_products: int = Field(default=200, env="NUM_PRODUCTS")
    max_orders_per_user: int = Field(default=5, env="MAX_ORDERS_PER_USER")
    max_reviews_per_product: int = Field(default=10, env="MAX_REVIEWS_PER_PRODUCT")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Performance settings
    batch_size: int = Field(default=50, env="BATCH_SIZE")
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


class Settings:
    """Main settings class that combines all configuration sections."""
    
    def __init__(self):
        # Create settings after dotenv is loaded
        self.database = DatabaseConfig()
        self.janusgraph = JanusGraphConfig()
        self.app = ApplicationConfig()
    
    @property
    def is_cloud_scylla(self) -> bool:
        """Check if we're connecting to a cloud ScyllaDB instance."""
        return self.database.host != "localhost" and self.database.ssl_enabled


# Create global settings instance after dotenv is loaded
settings = Settings()
