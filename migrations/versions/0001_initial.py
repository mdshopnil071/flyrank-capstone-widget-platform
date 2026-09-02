"""Create the widget platform schema."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("tenants",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_index("ix_tenants_email", "tenants", ["email"], unique=True)
    op.create_table("widgets",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String()),
        sa.Column("button_text", sa.String()),
        sa.Column("widget_type", sa.String(), nullable=False),
        sa.Column("form_fields", sa.JSON(), nullable=False),
        sa.Column("display_options", sa.JSON(), nullable=False),
    )
    op.create_table("submissions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("widget_id", sa.String(), sa.ForeignKey("widgets.id"), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("geo_data", sa.JSON()),
        sa.Column("idempotency_key", sa.String()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_index("uq_submission_widget_idempotency", "submissions", ["widget_id", "idempotency_key"], unique=True)
    op.create_index("ix_submissions_widget_created", "submissions", ["widget_id", "created_at"])


def downgrade():
    op.drop_index("ix_submissions_widget_created", table_name="submissions")
    op.drop_index("uq_submission_widget_idempotency", table_name="submissions")
    op.drop_table("submissions")
    op.drop_table("widgets")
    op.drop_index("ix_tenants_email", table_name="tenants")
    op.drop_table("tenants")
