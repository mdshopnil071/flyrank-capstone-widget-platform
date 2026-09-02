from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Widget, Submission, Tenant
from app.schemas import SubmissionOut
from app.auth import get_current_tenant

router = APIRouter(prefix="/api/dashboard", tags=["Owner Dashboard"])

@router.get("/submissions", response_model=List[SubmissionOut])
def list_owner_submissions(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    # Query returns submissions exclusively owned by current tenant
    submissions = (
        db.query(Submission)
        .join(Widget)
        .filter(Widget.tenant_id == current_tenant.id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    return submissions

@router.get("/stats")
def get_dashboard_stats(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    total_widgets = db.query(Widget).filter(Widget.tenant_id == current_tenant.id).count()
    total_submissions = (
        db.query(Submission)
        .join(Widget)
        .filter(Widget.tenant_id == current_tenant.id)
        .count()
    )
    return {
        "total_widgets": total_widgets,
        "total_submissions": total_submissions
    }

@router.get("/widgets/{widget_id}/stats")
def get_widget_stats(
    widget_id: str,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    widget = db.query(Widget).filter(Widget.id == widget_id, Widget.tenant_id == current_tenant.id).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    total = db.query(Submission).filter(Submission.widget_id == widget_id).count()
    by_country = (
        db.query(Submission.geo_data, func.count(Submission.id))
        .filter(Submission.widget_id == widget_id)
        .group_by(Submission.geo_data)
        .all()
    )
    return {
        "widget_id": widget_id,
        "total_submissions": total,
        "geo_breakdown": [{"geo": geo, "count": count} for geo, count in by_country],
    }