#!/usr/bin/env python3
"""
Repository Service Example

This example demonstrates how to use the RepositoryService for repository management.
"""

import os
from dotenv import load_dotenv
from config.settings import Settings
from core.services.repository import RepositoryService
from core.models.repository import RepositoryStatus

# Load environment variables
load_dotenv()

def main():
    """
    Example usage of RepositoryService for repository management.
    """
    
    print("=== Repository Service Example ===")
    
    # Load configuration
    settings = Settings()
    
    print(f"Configuration loaded:")
    print(f"  Metadata DB: {settings.metadata_db.config.type}")
    print()
    
    # Create repository service
    repo_service = RepositoryService(settings)
    
    try:
        # Example 1: Get all repositories
        print("=== Example 1: Get all repositories ===")
        repositories = repo_service.get_all_repositories()
        
        print(f"Found {len(repositories)} repositories:")
        for repo in repositories:
            print(f"  - {repo.name} ({repo.repo_status.value})")
        print()
        
        # Example 2: Create a new repository
        print("=== Example 2: Create new repository ===")
        
        new_repo = repo_service.create_repository(
            name="example-repo",
            description="An example repository for testing",
            repo="/example/repo",
            repo_url="https://github.com/example/repo",
            repo_status=RepositoryStatus.PENDING
        )
        
        if new_repo:
            print(f"Created repository: {new_repo.name} (ID: {new_repo.id})")
            
            # Example 3: Update repository status
            print("=== Example 3: Update repository status ===")
            success = repo_service.update_repository_status(
                new_repo.id, 
                RepositoryStatus.IN_PROGRESS
            )
            
            if success:
                print("Repository status updated successfully")
                
                # Example 4: Update repository counts
                print("=== Example 4: Update repository counts ===")
                success = repo_service.update_repository_counts(
                    new_repo.id,
                    tokens=1500,
                    snippets=25
                )
                
                if success:
                    print("Repository counts updated successfully")
                    
                    # Example 5: Get repository by name
                    print("=== Example 5: Get repository by name ===")
                    found_repo = repo_service.get_repository_by_name("example-repo")
                    
                    if found_repo:
                        print(f"Repository details:")
                        print(f"  Name: {found_repo.name}")
                        print(f"  Status: {found_repo.repo_status.value}")
                        print(f"  Tokens: {found_repo.tokens}")
                        print(f"  Snippets: {found_repo.snippets}")
                        print(f"  Created: {found_repo.created_at}")
                        print()
                        
                        # Example 6: Get repositories by status
                        print("=== Example 6: Get repositories by status ===")
                        in_progress_repos = repo_service.get_repositories_by_status(
                            RepositoryStatus.IN_PROGRESS
                        )
                        
                        print(f"Repositories in progress: {len(in_progress_repos)}")
                        for repo in in_progress_repos:
                            print(f"  - {repo.name}")
                        print()
            
            # Example 7: Clean up - delete the test repository
            print("=== Example 7: Clean up test repository ===")
            success = repo_service.delete_repository(new_repo.id)
            
            if success:
                print("Test repository deleted successfully")
            else:
                print("Failed to delete test repository")
        else:
            print("Failed to create repository")
    
    except Exception as e:
        print(f"Error during repository operations: {e}")
    
    finally:
        # Close the service
        repo_service.close()
        print("Repository service closed")

if __name__ == "__main__":
    main()
