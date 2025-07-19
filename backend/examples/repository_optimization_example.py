#!/usr/bin/env python3
"""
Example demonstrating the optimized RepositoryService initialization.

This example shows the benefits of initializing the database session
directly in __init__ instead of lazy initialization.
"""

import time
from config.settings import Settings
from core.services.repository import RepositoryService

def demonstrate_repository_optimization():
    """Demonstrate the optimized RepositoryService initialization"""
    
    print("🚀 RepositoryService Optimization Example")
    print("=" * 50)
    
    print("\n⚡ 1. Initialization Performance")
    print("-" * 35)
    
    # Measure initialization time
    start_time = time.time()
    settings = Settings()
    repository_service = RepositoryService(settings)
    init_time = time.time() - start_time
    
    print(f"✅ Service initialized in {init_time:.3f} seconds")
    print("✅ Database session ready immediately")
    
    print("\n📊 2. Method Call Performance")
    print("-" * 30)
    
    # Test multiple method calls without initialization overhead
    methods_to_test = [
        ("get_all_repositories", lambda: repository_service.get_all_repositories()),
        ("search_repositories", lambda: repository_service.search_repositories("test")),
        ("get_repository_by_name", lambda: repository_service.get_repository_by_name("nonexistent")),
    ]
    
    for method_name, method_call in methods_to_test:
        start_time = time.time()
        try:
            result = method_call()
            call_time = time.time() - start_time
            result_count = len(result) if isinstance(result, list) else (1 if result else 0)
            print(f"✅ {method_name}: {call_time:.3f}s, {result_count} results")
        except Exception as e:
            call_time = time.time() - start_time
            print(f"❌ {method_name}: {call_time:.3f}s, Error: {e}")
    
    print("\n🎯 3. Optimization Benefits")
    print("-" * 25)
    print("✅ No lazy initialization overhead")
    print("✅ Database session created once at startup")
    print("✅ Cleaner method implementations")
    print("✅ No need for _initialize_db_session() calls")
    print("✅ Consistent performance across all methods")
    print("✅ Fail-fast if database connection issues")
    
    print("\n🔧 4. Code Comparison")
    print("-" * 20)
    print("BEFORE (Lazy Initialization):")
    print("""
    def __init__(self, settings):
        self.settings = settings
        self._db_session: Optional[Session] = None
    
    def _initialize_db_session(self):
        if self._db_session is None:
            self._db_session = ServiceFactory.create_db_session(...)
    
    def get_all_repositories(self):
        self._initialize_db_session()  # Called every time!
        return self._db_session.query(Repository).all()
    """)
    
    print("\nAFTER (Direct Initialization):")
    print("""
    def __init__(self, settings):
        self.settings = settings
        self._db_session: Session = ServiceFactory.create_db_session(...)
    
    def get_all_repositories(self):
        return self._db_session.query(Repository).all()  # Direct use!
    """)
    
    print("\n📈 5. Performance Impact")
    print("-" * 25)
    print("✅ Eliminated redundant initialization checks")
    print("✅ Reduced method call overhead")
    print("✅ Simplified error handling")
    print("✅ Better type safety (Session vs Optional[Session])")
    print("✅ Cleaner, more readable code")
    
    print("\n🎉 6. Architecture Benefits")
    print("-" * 25)
    print("✅ Follows 'fail-fast' principle")
    print("✅ Consistent with other services")
    print("✅ Easier to test and mock")
    print("✅ Reduced cognitive complexity")
    print("✅ Better IDE support and type checking")

if __name__ == "__main__":
    demonstrate_repository_optimization()
