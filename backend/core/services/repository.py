"""
Repository Service

This service handles repository metadata management operations.
It provides a unified interface for repository CRUD operations using SQLAlchemy ORM.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from config.settings import Settings
from core.factories.service import ServiceFactory
from core.models.repository import Repository, RepositoryStatus


class RepositoryService:
    """
    Repository management service.
    
    This service provides a unified interface for:
    - Repository CRUD operations
    - Repository status management
    - Repository statistics tracking
    - Integration with metadata database
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize RepositoryService with configuration.
        
        Args:
            settings: Application settings containing database configuration
        """
        self.settings = settings
        print("Initializing database session...")
        self._db_session: Session = ServiceFactory.create_db_session(
            self.settings.metadata_db
        )
        print("✅ Database session initialized successfully")
    
    def get_all_repositories(self) -> List[Repository]:
        """
        Get all repositories.
        
        Returns:
            List of all Repository objects
        """
        try:
            repositories = self._db_session.query(Repository).order_by(Repository.name).all()
            print(f"✅ Retrieved {len(repositories)} repositories")
            return repositories
        except Exception as e:
            print(f"❌ Failed to get repositories: {e}")
            return []
    
    def get_repository_by_name(self, name: str) -> Optional[Repository]:
        """
        Get repository by name.
        
        Args:
            name: Repository name
            
        Returns:
            Repository object if found, None otherwise
        """
        try:
            repository = self._db_session.query(Repository).filter(Repository.name == name).first()
            if repository:
                print(f"✅ Found repository: {name}")
            else:
                print(f"❌ Repository not found: {name}")
            return repository
        except Exception as e:
            print(f"❌ Failed to get repository by name '{name}': {e}")
            return None
    
    def get_repository_by_path(self, repo_path: str) -> Optional[Repository]:
        """
        Get repository by path.
        
        Args:
            repo_path: Repository path (e.g., /owner/repo)
            
        Returns:
            Repository object if found, None otherwise
        """
        try:
            repository = self._db_session.query(Repository).filter(Repository.repo == repo_path).first()
            if repository:
                print(f"✅ Found repository by path: {repo_path}")
            else:
                print(f"❌ Repository not found by path: {repo_path}")
            return repository
        except Exception as e:
            print(f"❌ Failed to get repository by path '{repo_path}': {e}")
            return None
    
    def get_repository_by_id(self, repo_id: int) -> Optional[Repository]:
        """
        Get repository by ID.
        
        Args:
            repo_id: Repository ID
            
        Returns:
            Repository object if found, None otherwise
        """
        try:
            repository = self._db_session.query(Repository).filter(Repository.id == repo_id).first()
            if repository:
                print(f"✅ Found repository by ID: {repo_id}")
            else:
                print(f"❌ Repository not found by ID: {repo_id}")
            return repository
        except Exception as e:
            print(f"❌ Failed to get repository by ID {repo_id}: {e}")
            return None
    
    def create_repository(
        self, 
        name: str, 
        description: str, 
        repo: str, 
        repo_url: str, 
        repo_status: RepositoryStatus = RepositoryStatus.PENDING,
        tokens: int = 0,
        snippets: int = 0
    ) -> Optional[Repository]:
        """
        Create a new repository.
        
        Args:
            name: Repository name (must be unique)
            description: Repository description
            repo: Repository path
            repo_url: Repository URL
            repo_status: Repository status
            tokens: Token count
            snippets: Snippet count
            
        Returns:
            Created Repository object if successful, None otherwise
        """
        try:
            repository = Repository(
                name=name,
                description=description,
                repo=repo,
                repo_url=repo_url,
                repo_status=repo_status,
                tokens=tokens,
                snippets=snippets
            )
            
            self._db_session.add(repository)
            self._db_session.commit()
            
            print(f"✅ Created repository: {name}")
            return repository
            
        except IntegrityError as e:
            self._db_session.rollback()
            print(f"❌ Repository name already exists: {name}")
            return None
        except Exception as e:
            self._db_session.rollback()
            print(f"❌ Failed to create repository '{name}': {e}")
            return None
    
    def search_repositories(self, search_term: str) -> List[Repository]:
        """
        Search repositories by name or repo path.
        
        Args:
            search_term: Term to search for in name or repo fields
            
        Returns:
            List of matching Repository objects
        """
        try:
            # Use LIKE for fuzzy matching on both name and repo fields
            search_pattern = f"%{search_term}%"
            repositories = self._db_session.query(Repository).filter(
                (Repository.name.like(search_pattern)) | 
                (Repository.repo.like(search_pattern))
            ).order_by(Repository.name).all()
            
            print(f"✅ Found {len(repositories)} repositories matching '{search_term}'")
            return repositories
            
        except Exception as e:
            print(f"❌ Failed to search repositories with term '{search_term}': {e}")
            return []
    
    def update_repository(
        self, 
        repo_id: int, 
        name: Optional[str] = None,
        description: Optional[str] = None,
        repo: Optional[str] = None,
        repo_url: Optional[str] = None
    ) -> bool:
        """
        Update repository information.
        
        Args:
            repo_id: Repository ID
            name: New name (optional)
            description: New description (optional)
            repo: New repo path (optional)
            repo_url: New repo URL (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repository = self._db_session.query(Repository).filter(Repository.id == repo_id).first()
            if not repository:
                print(f"❌ Repository not found: ID {repo_id}")
                return False
            
            # Update only provided fields
            if name is not None:
                repository.name = name
            if description is not None:
                repository.description = description
            if repo is not None:
                repository.repo = repo
            if repo_url is not None:
                repository.repo_url = repo_url
            
            self._db_session.commit()
            print(f"✅ Updated repository: ID {repo_id}")
            return True
            
        except IntegrityError as e:
            self._db_session.rollback()
            print(f"❌ Update failed due to constraint violation: {e}")
            return False
        except Exception as e:
            self._db_session.rollback()
            print(f"❌ Failed to update repository ID {repo_id}: {e}")
            return False
    
    def update_repository_status(self, repo_id: int, status: RepositoryStatus) -> bool:
        """
        Update repository status.
        
        Args:
            repo_id: Repository ID
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repository = self._db_session.query(Repository).filter(Repository.id == repo_id).first()
            if not repository:
                print(f"❌ Repository not found: ID {repo_id}")
                return False
            
            repository.repo_status = status
            self._db_session.commit()
            
            print(f"✅ Updated repository status: ID {repo_id} -> {status.value}")
            return True
            
        except Exception as e:
            self._db_session.rollback()
            print(f"❌ Failed to update repository status ID {repo_id}: {e}")
            return False
    
    def update_repository_counts(self, repo_id: int, tokens: int, snippets: int) -> bool:
        """
        Update repository token and snippet counts.
        
        Args:
            repo_id: Repository ID
            tokens: Token count
            snippets: Snippet count
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repository = self._db_session.query(Repository).filter(Repository.id == repo_id).first()
            if not repository:
                print(f"❌ Repository not found: ID {repo_id}")
                return False
            
            repository.tokens = tokens
            repository.snippets = snippets
            self._db_session.commit()
            
            print(f"✅ Updated repository counts: ID {repo_id} -> tokens: {tokens}, snippets: {snippets}")
            return True
            
        except Exception as e:
            self._db_session.rollback()
            print(f"❌ Failed to update repository counts ID {repo_id}: {e}")
            return False
    
    def delete_repository(self, repo_id: int) -> bool:
        """
        Delete repository.
        
        Args:
            repo_id: Repository ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repository = self._db_session.query(Repository).filter(Repository.id == repo_id).first()
            if not repository:
                print(f"❌ Repository not found: ID {repo_id}")
                return False
            
            repo_name = repository.name
            self._db_session.delete(repository)
            self._db_session.commit()
            
            print(f"✅ Deleted repository: {repo_name} (ID {repo_id})")
            return True
            
        except Exception as e:
            self._db_session.rollback()
            print(f"❌ Failed to delete repository ID {repo_id}: {e}")
            return False
    
    def get_repositories_by_status(self, status: RepositoryStatus) -> List[Repository]:
        """
        Get repositories by status.
        
        Args:
            status: Repository status to filter by
            
        Returns:
            List of Repository objects with the specified status
        """
        try:
            repositories = self._db_session.query(Repository).filter(
                Repository.repo_status == status
            ).order_by(Repository.name).all()
            
            print(f"✅ Found {len(repositories)} repositories with status: {status.value}")
            return repositories
            
        except Exception as e:
            print(f"❌ Failed to get repositories by status '{status.value}': {e}")
            return []
    
    def close(self):
        """Close database session if open"""
        if self._db_session:
            self._db_session.close()
            print("Database session closed")
