from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.models import Widget, Submission
from app.schemas import PublicSubmissionPayload
from app.services.geo import get_ip_geolocation
from app.services.notification import send_owner_notification
from app.config import settings

limiter = Limiter(key_func=get_remote_address)
widget_limiter = Limiter(key_func=lambda request: f"{get_remote_address(request)}:{request.path.split('/')[4]}")
router = APIRouter(prefix="/api/public", tags=["Public Widget Execution"])

@router.get("/widgets/{widget_id}/config")
def get_widget_config(widget_id: str, response: Response, db: Session = Depends(get_db)):
    widget = db.query(Widget).filter(Widget.id == widget_id).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget configuration unavailable")
    
    # Public caching policy implementation
    response.headers["Cache-Control"] = "public, max-age=300"
    return {
        "id": widget.id,
        "title": widget.title,
        "description": widget.description,
        "button_text": widget.button_text,
        "widget_type": widget.widget_type,
        "form_fields": widget.form_fields,
        "display_options": widget.display_options
    }

@router.post("/widgets/{widget_id}/submit", status_code=201)
@limiter.limit("5/minute")  # Rate limit enforcement
@widget_limiter.limit("20/hour")
async def submit_widget_data(
    widget_id: str,
    payload: PublicSubmissionPayload,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Spam control via honeypot evaluation
    if payload.website_hp:
        return {"status": "success", "message": "Submission received"}

    widget = db.query(Widget).filter(Widget.id == widget_id).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Target widget not found")

    idempotency_key = request.headers.get("Idempotency-Key")
    if idempotency_key:
        existing = db.query(Submission).filter(
            Submission.widget_id == widget_id,
            Submission.idempotency_key == idempotency_key,
        ).first()
        if existing:
            return {"status": "success", "id": existing.id, "geo": existing.geo_data, "deduplicated": True}

    client_ip = request.client.host
    geo_info = await get_ip_geolocation(client_ip)

    submission = Submission(
        widget_id=widget.id,
        payload={"name": payload.name, "email": payload.email, "message": payload.message},
        geo_data=geo_info,
        idempotency_key=idempotency_key,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # Trigger isolated notification side effect
    if widget.owner:
        background_tasks.add_task(send_owner_notification, widget.owner.email, submission.id)

    return {"status": "success", "id": submission.id, "geo": geo_info}