"""
Modules for enhanced bot features including RAG memory, mood system, and relationships.
"""

# Note: Avoid importing chromadb-dependent modules at package level to support testing
# Import them directly where needed

__all__ = ['RAGEngine', 'MoodManager', 'Mood', 'RelationshipManager', 'PersonaStateStore', 'PromptComposer']
