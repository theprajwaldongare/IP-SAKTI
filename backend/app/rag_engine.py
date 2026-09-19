"""
RAG Engine for Ayurvedic IP & Regulatory Knowledge Base.
Performs semantic index search, context extraction, relevance scoring,
and snippet compilation for prompt augmentation.
"""

import math
import re
from typing import List, Dict, Any
from app.kb_data import KNOWLEDGE_BASE, AYURVEDIC_IPC_GLOSSARY

def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text."""
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    stop_words = {"the", "a", "an", "and", "or", "in", "on", "at", "for", "with", "is", "of", "to", "by", "this", "that", "it"}
    return [t for t in tokens if t not in stop_words and len(t) > 1]

class SimpleTFIDFIndex:
    """Lightweight TF-IDF & Keyword Vector Index for zero-config fast retrieval."""
    def __init__(self, documents: List[Dict[str, Any]]):
        self.documents = documents
        self.doc_tokens = []
        self.df = {}
        self.total_docs = len(documents)
        
        for doc in documents:
            text = f"{doc['title']} {doc['category']} {' '.join(doc['keywords'])} {doc['content']}"
            tokens = list(set(tokenize(text)))
            self.doc_tokens.append(tokens)
            for t in tokens:
                self.df[t] = self.df.get(t, 0) + 1

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return self.documents[:top_k]

        scores = []
        for idx, doc in enumerate(self.documents):
            score = 0.0
            doc_tokens = self.doc_tokens[idx]
            
            # Check title / keyword match bonuses
            title_text = doc["title"].lower()
            keyword_text = " ".join(doc["keywords"]).lower()
            category_text = doc["category"].lower()
            
            for qt in query_tokens:
                if qt in title_text:
                    score += 5.0
                if qt in keyword_text:
                    score += 3.0
                if qt in category_text:
                    score += 2.0
                
                # TF-IDF match
                if qt in doc_tokens:
                    tf = doc_tokens.count(qt)
                    idf = math.log((self.total_docs + 1) / (self.df.get(qt, 0) + 1)) + 1
                    score += tf * idf

            scores.append((score, idx))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, idx in scores[:top_k]:
            if score > 0:
                doc_copy = dict(self.documents[idx])
                doc_copy["relevance_score"] = round(score, 2)
                results.append(doc_copy)
        
        # If no positive matches, fallback to top items
        if not results:
            results = [dict(d, relevance_score=0.5) for d in self.documents[:top_k]]
            
        return results

# Initialize singleton RAG index
rag_index = SimpleTFIDFIndex(KNOWLEDGE_BASE)

def retrieve_context(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Retrieve domain context and relevant glossary entities for a query.
    """
    retrieved_docs = rag_index.search(query, top_k=top_k)
    
    # Check for ingredient matches in glossary
    query_lower = query.lower()
    matched_ingredients = []
    for name, details in AYURVEDIC_IPC_GLOSSARY.items():
        if name in query_lower or details["sanskrit"].lower() in query_lower or details["latin"].lower() in query_lower:
            matched_ingredients.append({"ingredient": name, **details})
            
    formatted_context = ""
    citations = []
    
    for doc in retrieved_docs:
        # FIX: Use .get() to prevent KeyError if 'source' is missing from kb_data
        doc_source = doc.get("source", "Official Legal Guidelines")
        
        formatted_context += f"--- SOURCE [{doc['id']}]: {doc['title']} ({doc_source}) ---\n"
        formatted_context += f"{doc['content']}\n\n"
        citations.append({
            "id": doc["id"],
            "title": doc["title"],
            "source": doc_source,
            "relevance": doc.get("relevance_score", 1.0)
        })
        
    return {
        "context_str": formatted_context,
        "docs": retrieved_docs,
        "citations": citations,
        "matched_ingredients": matched_ingredients
    }

# def retrieve_context(query: str, top_k: int = 3) -> Dict[str, Any]:
#     """
#     Retrieve domain context and relevant glossary entities for a query.
#     """
#     retrieved_docs = rag_index.search(query, top_k=top_k)
    
#     # Check for ingredient matches in glossary
#     query_lower = query.lower()
#     matched_ingredients = []
#     for name, details in AYURVEDIC_IPC_GLOSSARY.items():
#         if name in query_lower or details["sanskrit"].lower() in query_lower or details["latin"].lower() in query_lower:
#             matched_ingredients.append({"ingredient": name, **details})
            
#     formatted_context = ""
#     citations = []
    
#     for doc in retrieved_docs:
#         formatted_context += f"--- SOURCE [{doc['id']}]: {doc['title']} ({doc['source']}) ---\n"
#         formatted_context += f"{doc['content']}\n\n"
#         citations.append({
#             "id": doc["id"],
#             "title": doc["title"],
#             "source": doc["source"],
#             "relevance": doc.get("relevance_score", 1.0)
#         })
        
#     return {
#         "context_str": formatted_context,
#         "docs": retrieved_docs,
#         "citations": citations,
#         "matched_ingredients": matched_ingredients
#     }
