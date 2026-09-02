from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Widget, Tenant
from app.schemas import WidgetCreate, WidgetOut, WidgetUpdate
from app.config import settings
from app.auth import get_current_tenant

router = APIRouter(prefix="/api/widgets", tags=["Widget Management"])

@router.post("", response_model=WidgetOut, status_code=201)
def create_widget(
    data: WidgetCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    widget = Widget(
        tenant_id=current_tenant.id,
        title=data.title,
        description=data.description,
        button_text=data.button_text,
        widget_type=data.widget_type,
        form_fields=data.form_fields,
        display_options=data.display_options,
    )
    db.add(widget)
    db.commit()
    db.refresh(widget)
    return widget

@router.patch("/{widget_id}", response_model=WidgetOut)
def update_widget(
    widget_id: str,
    data: WidgetUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    widget = db.query(Widget).filter(Widget.id == widget_id, Widget.tenant_id == current_tenant.id).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found or unauthorized")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(widget, field, value)
    db.commit()
    db.refresh(widget)
    return widget

@router.get("/{widget_id}/snippet")
def get_embed_snippet(widget_id: str, request: Request, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    widget = db.query(Widget).filter(Widget.id == widget_id, Widget.tenant_id == current_tenant.id).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found or unauthorized")
    base_url = str(request.base_url).rstrip("/")
    return {"widget_id": widget.id, "snippet": f'<script src="{base_url}/static/widget.v1.js?id={widget.id}"></script>'}

@router.get("", response_model=List[WidgetOut])
def get_widgets(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    # Enforce multi-tenant isolation
    return db.query(Widget).filter(Widget.tenant_id == current_tenant.id).all()

@router.get("/{widget_id}", response_model=WidgetOut)
def get_widget(
    widget_id: str,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    widget = db.query(Widget).filter(Widget.id == widget_id, Widget.tenant_id == current_tenant.id).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found or unauthorized")
    return widget

@router.delete("/{widget_id}", status_code=204)
def delete_widget(
    widget_id: str,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    widget = db.query(Widget).filter(Widget.id == widget_id, Widget.tenant_id == current_tenant.id).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found or unauthorized")
    db.delete(widget)
    db.commit()
    return None