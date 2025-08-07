from typing import Optional, Dict
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from config.settings import Settings
import logging

logger = logging.getLogger(__name__)

class DatabaseRouter:
    """Database router for managing public, user management, and user private database connections"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.public_session = None
        self.users_session = None
        self.user_sessions: Dict[str, Session] = {}
        self._initialize_sessions()
    
    def _initialize_sessions(self):
        """Initialize public database and user management database sessions"""
        try:
            # Public database session (doc2dev)
            public_config = self._get_db_config("doc2dev")
            public_engine = create_engine(public_config)
            PublicSessionLocal = sessionmaker(bind=public_engine)
            self.public_session = PublicSessionLocal()
            
            # User management database session (doc2dev_users)
            users_config = self._get_db_config("doc2dev_users")
            users_engine = create_engine(users_config)
            UsersSessionLocal = sessionmaker(bind=users_engine)
            self.users_session = UsersSessionLocal()
            
            logger.info("Database sessions initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database sessions: {e}")
            raise
    
    def _get_db_config(self, database_name: str) -> str:
        """Generate database connection string for given database name"""
        db_config = self.settings.metadata_db.config
        return f"mysql+pymysql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{database_name}"
    
    def get_user_db_name(self, user_id: str) -> str:
        """Generate user-specific database name from user ID"""
        # Replace hyphens with underscores for MySQL compatibility
        safe_user_id = user_id.replace('-', '_')
        return f"doc2dev_user_{safe_user_id}"
    
    def get_session(self, user_id: Optional[str] = None) -> Session:
        """Get database session based on user context (public or private)"""
        if user_id is None:
            return self.public_session
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = self._create_user_session(user_id)
        
        return self.user_sessions[user_id]
    
    def get_users_session(self) -> Session:
        """Get user management database session"""
        return self.users_session
    
    def _create_user_session(self, user_id: str) -> Session:
        """Create database session for specific user"""
        user_config = self._get_db_config(self.get_user_db_name(user_id))
        user_engine = create_engine(user_config)
        UserSessionLocal = sessionmaker(bind=user_engine)
        return UserSessionLocal()
    
    def create_user_database(self, user_id: str) -> str:
        """Create user-specific database and initialize table structure"""
        db_name = self.get_user_db_name(user_id)
        
        try:
            # Create database using admin privileges
            admin_session = self.public_session
            admin_session.execute(text(f"CREATE DATABASE {db_name}"))
            admin_session.commit()
            
            # Initialize table structure
            user_session = self._create_user_session(user_id)
            self._initialize_user_tables(user_session)
            
            logger.info(f"Created user database: {db_name}")
            return db_name
            
        except Exception as e:
            logger.error(f"Failed to create user database {db_name}: {e}")
            raise
    
    def _initialize_user_tables(self, session: Session):
        """Initialize table structure in user database"""
        # Create repositories table
        session.execute(text("""
            CREATE TABLE repositories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                description VARCHAR(500),
                repo VARCHAR(255) NOT NULL,
                repo_url VARCHAR(255) NOT NULL,
                tokens INT NOT NULL,
                snippets INT NOT NULL,
                repo_status ENUM('in_progress', 'completed', 'failed', 'pending') NOT NULL,
                source ENUM('github', 'gitlab') NOT NULL DEFAULT 'github',
                created_at TIMESTAMP DEFAULT UTC_TIMESTAMP(),
                updated_at TIMESTAMP DEFAULT UTC_TIMESTAMP() ON UPDATE UTC_TIMESTAMP()
            )
        """))
        session.commit()
        logger.info("User database tables initialized successfully")
    
    def database_exists(self, user_id: str) -> bool:
        """Check if user database exists"""
        try:
            test_session = self._create_user_session(user_id)
            test_session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
