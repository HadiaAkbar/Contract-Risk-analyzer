from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Document, DocumentChunk
from app.schemas import SearchQuery, SearchResult
from app.auth import get_current_user
from app.semantic_search import search_chunks
from app.ai_engine import answer_query_with_llm

router = APIRouter(prefix="/search", tags=["Semantic Search"])


@router.post("", response_model=list[SearchResult])
def search_document(payload: SearchQuery, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == payload.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user.role != "admin" and doc.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == doc.id
    ).order_by(DocumentChunk.chunk_index).all()

    if not chunks:
        raise HTTPException(status_code=400, detail="Document has not been analyzed/chunked yet")

    texts = [c.text for c in chunks]
    results = search_chunks(texts, payload.query, payload.top_k)
    return [SearchResult(chunk_index=idx, text=text, score=score) for idx, text, score in results]


@router.post("/ask")
def ask_document(payload: SearchQuery, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    """Bonus: RAG-style natural language Q&A over the document (LLM required)."""
    doc = db.query(Document).filter(Document.id == payload.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user.role != "admin" and doc.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    answer = answer_query_with_llm(doc.raw_text or "", payload.query)
    if answer is None:
        raise HTTPException(
            status_code=503,
            detail="LLM Q&A unavailable (no ANTHROPIC_API_KEY configured). Use /search instead."
        )
    return {"question": payload.query, "answer": answer}
