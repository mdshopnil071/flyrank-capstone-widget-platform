from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime

class TenantCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class Token(BaseModel):
    access_token: str
    token_type: str

class WidgetCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    button_text: Optional[str] = Field(default="Submit", min_length=1, max_length=60)
    widget_type: Literal["signup", "cta", "popover"] = "signup"
    form_fields: List[Dict[str, Any]] = Field(default_factory=list, max_length=20)
    display_options: Dict[str, Any] = Field(default_factory=dict)

class WidgetUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    button_text: Optional[str] = Field(default=None, min_length=1, max_length=60)
    widget_type: Optional[Literal["signup", "cta", "popover"]] = None
    form_fields: Optional[List[Dict[str, Any]]] = Field(default=None, max_length=20)
    display_options: Optional[Dict[str, Any]] = None

class WidgetOut(BaseModel):
    id: str
    tenant_id: str
    title: str
    description: Optional[str]
    button_text: str
    widget_type: str
    form_fields: List[Dict[str, Any]]
    display_options: Dict[str, Any]

    class Config:
        from_attributes = True

class PublicSubmissionPayload(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    message: Optional[str] = Field(default=None, max_length=2000)
    website_hp: Optional[str] = Field(default=None, max_length=200)

    model_config = {"extra": "forbid"}

class SubmissionOut(BaseModel):
    id: str
    widget_id: str
    payload: Dict[str, Any]
    geo_data: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True