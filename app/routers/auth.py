from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Tenant
from app.schemas import TenantCreate, Token
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", status_code=201)
def register(tenant_data: TenantCreate, db: Session = Depends(get_db)):
    existing = db.query(Tenant).filter(Tenant.email == tenant_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_tenant = Tenant(
        email=tenant_data.email,
        password_hash=hash_password(tenant_data.password)
    )
    db.add(new_tenant)
    db.commit()
    return {"message": "Tenant account registered successfully"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.email == form_data.username).first()
    if not tenant or not verify_password(form_data.password, tenant.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": tenant.id})
    return {"access_token": access_token, "token_type": "bearer"}