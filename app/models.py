import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    widgets = relationship("Widget", back_populates="owner", cascade="all, delete-orphan")

class Widget(Base):
    __tablename__ = "widgets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    button_text = Column(String, default="Submit")
    widget_type = Column(String, nullable=False, default="signup")
    form_fields = Column(JSON, nullable=False, default=list)
    display_options = Column(JSON, nullable=False, default=dict)

    owner = relationship("Tenant", back_populates="widgets")
    submissions = relationship("Submission", back_populates="widget", cascade="all, delete-orphan")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    widget_id = Column(String, ForeignKey("widgets.id"), nullable=False)
    payload = Column(JSON, nullable=False)
    geo_data = Column(JSON, nullable=True)
    idempotency_key = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    widget = relationship("Widget", back_populates="submissions")

    __table_args__ = (
        UniqueConstraint("widget_id", "idempotency_key", name="uq_submission_widget_idempotency"),
        Index("ix_submissions_widget_created", "widget_id", "created_at"),
    )