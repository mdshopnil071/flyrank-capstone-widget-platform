from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Tenant, Widget


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.email == "demo@example.com").first()
        if not tenant:
            tenant = Tenant(email="demo@example.com", password_hash=hash_password("demo-password-123"))
            db.add(tenant)
            db.flush()
        if not tenant.widgets:
            db.add(Widget(
                tenant_id=tenant.id,
                title="Newsletter signup",
                description="Get practical engineering notes every week.",
                button_text="Join the list",
                widget_type="signup",
                form_fields=[{"name": "name", "type": "text"}, {"name": "email", "type": "email"}],
                display_options={"theme": "light"},
            ))
        db.commit()
        print("Seeded demo@example.com / demo-password-123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
