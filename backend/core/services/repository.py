"""
Repository Service

This service handles repository metadata management operations.
It provides a unified interface for repository CRUD operations using SQLAlchemy ORM.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from core.models.repository import Repository, RepositoryStatus, RepositorySource


class RepositoryService:
    """
    Repository management service.
    
    This service provides a unified interface for:
    - Repository CRUD operations
    - Repository status management
    - Repository statistics tracking
    - Integration with metadata database
    """
    
    def __init__(self, db_router):
        """
        Initialize RepositoryService with database router.
        
        Args:
            db_router: DatabaseRouter instance for multi-tenant database access
        """
        self.db_router = db_router
        print("Initializing database session...")
        # Use public database session for repository metadata
        self._db_session: Session = self.db_router.public_session
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

    def get_user_repositories(self, user_id: str) -> List[Repository]:
        """
        Get repositories for a specific user from their private database.

        Args:
            user_id: User ID to get repositories for

        Returns:
            List of Repository objects for the user
        """
        try:
            # Get user-specific database session
            user_session = self.db_router.get_session(user_id)
            repositories = user_session.query(Repository).order_by(Repository.name).all()
            print(f"✅ Retrieved {len(repositories)} repositories for user {user_id}")
            return repositories
        except Exception as e:
            print(f"❌ Failed to get repositories for user {user_id}: {e}")
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

    def get_user_repository_by_path(self, user_id: str, repo_path: str) -> Optional[Repository]:
        """
        Get repository by path for a specific user from their private database.

        Args:
            user_id: User ID
            repo_path: Repository path (e.g., /owner/repo)

        Returns:
            Repository object if found, None otherwise
        """
        try:
            user_session = self.db_router.get_session(user_id)
            repository = user_session.query(Repository).filter(Repository.repo == repo_path).first()
            if repository:
                print(f"✅ Found repository by path for user {user_id}: {repo_path}")
            else:
                print(f"❌ Repository not found by path for user {user_id}: {repo_path}")
            return repository
        except Exception as e:
            print(f"❌ Failed to get repository by path for user {user_id} '{repo_path}': {e}")
            return None

    def get_user_repository_by_id(self, user_id: str, repo_id: int) -> Optional[Repository]:
        """
        Get repository by ID from user's private database.

        Args:
            user_id: User ID
            repo_id: Repository ID

        Returns:
            Repository object if found, None otherwise
        """
        try:
            user_session = self.db_router.get_session(user_id)
            repository = user_session.query(Repository).filter(Repository.id == repo_id).first()
            if repository:
                print(f"✅ Found repository by ID for user {user_id}: {repo_id}")
            else:
                print(f"❌ Repository not found by ID for user {user_id}: {repo_id}")
            return repository
        except Exception as e:
            print(f"❌ Failed to get repository by ID for user {user_id} '{repo_id}': {e}")
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
        repo_status: RepositoryStatus = RepositoryStatus.pending,
        source: RepositorySource = RepositorySource.github,
        tokens: int = 0,
        snippets: int = 0
    ) -> Optional[int]:
        """
        Create a new repository.

        Args:
            name: Repository name (must be unique)
            description: Repository description
            repo: Repository path
            repo_url: Repository URL
            repo_status: Repository status
            source: Repository source platform (github/gitlab)
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
                source=source,
                tokens=tokens,
                snippets=snippets
            )
            
            self._db_session.add(repository)
            self._db_session.commit()
            
            print(f"✅ Created repository: {name}")
            return repository.id
            
        except IntegrityError as e:
            self._db_session.rollback()
            print(f"❌ Repository name already exists: {name}")
            return None
        except Exception as e:
            self._db_session.rollback()
            print(f"❌ Failed to create repository '{name}': {e}")
            return None

    def create_user_repository(
        self,
        user_id: str,
        name: str,
        description: str,
        repo: str,
        repo_url: str,
        repo_status: RepositoryStatus = RepositoryStatus.pending,
        source: RepositorySource = RepositorySource.github,
        tokens: int = 0,
        snippets: int = 0
    ) -> Optional[int]:
        """
        Create a new repository in user's private database.

        Args:
            user_id: User ID
            name: Repository name (must be unique within user's database)
            description: Repository description
            repo: Repository path
            repo_url: Repository URL
            repo_status: Repository status
            source: Repository source platform (github/gitlab)
            tokens: Token count
            snippets: Snippet count

        Returns:
            Created Repository ID if successful, None otherwise
        """
        try:
            user_session = self.db_router.get_session(user_id)
            repository = Repository(
                name=name,
                description=description,
                repo=repo,
                repo_url=repo_url,
                repo_status=repo_status,
                source=source,
                tokens=tokens,
                snippets=snippets
            )

            user_session.add(repository)
            user_session.commit()

            print(f"✅ Created repository for user {user_id}: {name}")
            return repository.id

        except IntegrityError as e:
            user_session.rollback()
            print(f"❌ Repository name already exists for user {user_id}: {name}")
            return None
        except Exception as e:
            user_session.rollback()
            print(f"❌ Failed to create repository for user {user_id} '{name}': {e}")
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

    def update_user_repository_status(self, user_id: str, repo_id: int, status: RepositoryStatus) -> bool:
        """
        Update repository status in user's private database.

        Args:
            user_id: User ID
            repo_id: Repository ID
            status: New status

        Returns:
            True if successful, False otherwise
        """
        try:
            user_session = self.db_router.get_session(user_id)
            repository = user_session.query(Repository).filter(Repository.id == repo_id).first()
            if not repository:
                print(f"❌ Repository not found for user {user_id}: ID {repo_id}")
                return False

            repository.repo_status = status
            repository.updated_at = datetime.now()
            user_session.commit()

            print(f"✅ Updated repository status for user {user_id}: ID {repo_id} -> {status.value}")
            return True

        except Exception as e:
            user_session.rollback()
            print(f"❌ Failed to update repository status for user {user_id} ID {repo_id}: {e}")
            return False

    def update_user_repository_counts(self, user_id: str, repo_id: int, tokens: int, snippets: int) -> bool:
        """
        Update repository token and snippet counts in user's private database.

        Args:
            user_id: User ID
            repo_id: Repository ID
            tokens: Token count
            snippets: Snippet count

        Returns:
            True if successful, False otherwise
        """
        try:
            user_session = self.db_router.get_session(user_id)
            repository = user_session.query(Repository).filter(Repository.id == repo_id).first()
            if not repository:
                print(f"❌ Repository not found for user {user_id}: ID {repo_id}")
                return False

            repository.tokens = tokens
            repository.snippets = snippets
            repository.updated_at = datetime.now()
            user_session.commit()

            print(f"✅ Updated repository counts for user {user_id}: ID {repo_id} -> tokens: {tokens}, snippets: {snippets}")
            return True

        except Exception as e:
            user_session.rollback()
            print(f"❌ Failed to update repository counts for user {user_id} ID {repo_id}: {e}")
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

    def delete_user_repository(self, user_id: str, repo_id: int) -> bool:
        """
        Delete repository from user's private database.

        Args:
            user_id: User ID
            repo_id: Repository ID

        Returns:
            True if successful, False otherwise
        """
        try:
            user_session = self.db_router.get_session(user_id)
            repository = user_session.query(Repository).filter(Repository.id == repo_id).first()
            if not repository:
                print(f"❌ Repository not found for user {user_id}: ID {repo_id}")
                return False

            repo_name = repository.name
            user_session.delete(repository)
            user_session.commit()

            print(f"✅ Deleted repository for user {user_id}: {repo_name} (ID {repo_id})")
            return True

        except Exception as e:
            user_session.rollback()
            print(f"❌ Failed to delete repository for user {user_id} ID {repo_id}: {e}")
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
    
    def delete_vector_table(self, table_name: str) -> bool:
        """
        Delete vector table from the database.
        
        Args:
            table_name: Name of the vector table to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Sanitize table name by replacing hyphens with underscores to avoid SQL syntax errors
            safe_table_name = table_name.replace('-', '_')
            
            # Use existing SQLAlchemy session to execute raw SQL
            sql = f"DROP TABLE IF EXISTS {safe_table_name}"
            self._db_session.execute(sql)
            self._db_session.commit()
            
            print(f"✅ Successfully deleted vector table: {safe_table_name}")
            return True
            
        except Exception as e:
            self._db_session.rollback()
            print(f"❌ Failed to delete vector table '{table_name}': {str(e)}")
            return False
    
    def close(self):
        """Close database session if open"""
        if self._db_session:
            self._db_session.close()
            print("Database session closed")
