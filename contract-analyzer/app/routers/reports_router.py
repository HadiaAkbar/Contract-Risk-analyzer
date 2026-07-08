import os
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models import User, Document, RiskFinding
from app.auth import get_current_user
from app.report_generator import generate_pdf_report, generate_docx_report

router = APIRouter(prefix="/reports", tags=["Reports"])

REPORTS_DIR = os.path.join(settings.UPLOAD_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def _analysis_dict(doc: Document, db: Session) -> dict:
    a = doc.analysis
    if not a:
        raise HTTPException(status_code=404, detail="Document has not been analyzed yet")
    risks = db.query(RiskFinding).filter(RiskFinding.document_id == doc.id).all()
    return {
        "contract_type": a.contract_type,
        "parties": a.parties,
        "effective_date": a.effective_date,
        "expiry_date": a.expiry_date,
        "payment_terms": a.payment_terms,
        "renewal_clause": a.renewal_clause,
        "confidentiality_clause": a.confidentiality_clause,
        "termination_clause": a.termination_clause,
        "responsibilities": a.responsibilities,
        "executive_summary": a.executive_summary,
        "recommended_actions": a.recommended_actions,
        "risk_score": a.risk_score,
        "engine_used": a.engine_used,
        "risks": [{
            "category": r.category, "title": r.title, "explanation": r.explanation,
            "severity": r.severity, "confidence": r.confidence,
        } for r in risks],
    }


def _get_doc(document_id: int, db: Session, user: User) -> Document:
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if user.role != "admin" and doc.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return doc


@router.get("/{document_id}/pdf")
def get_pdf_report(document_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    doc = _get_doc(document_id, db, current_user)
    analysis = _analysis_dict(doc, db)
    out_path = os.path.join(REPORTS_DIR, f"report_{doc.id}_{uuid.uuid4().hex[:8]}.pdf")
    generate_pdf_report(analysis, doc.filename, out_path)
    return FileResponse(out_path, filename=f"{doc.filename}_risk_report.pdf",
                         media_type="application/pdf")


@router.get("/{document_id}/docx")
def get_docx_report(document_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    doc = _get_doc(document_id, db, current_user)
    analysis = _analysis_dict(doc, db)
    out_path = os.path.join(REPORTS_DIR, f"report_{doc.id}_{uuid.uuid4().hex[:8]}.docx")
    generate_docx_report(analysis, doc.filename, out_path)
    return FileResponse(
        out_path, filename=f"{doc.filename}_risk_report.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
