from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, JSON, Text
from app.database.connection import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    complaint_source = Column(Text, nullable=True)
    customer_name = Column(Text, nullable=True)

    product_name = Column(Text, nullable=True)
    product_strength = Column(Text, nullable=True)

    batch_number = Column(Text, nullable=True)
    manufacturing_date = Column(Text, nullable=True)
    expiry_date = Column(Text, nullable=True)

    affected_quantity = Column(Text, nullable=True)

    complaint_type = Column(Text, nullable=True)
    complaint_description = Column(Text, nullable=True)

    severity = Column(Text, nullable=True)
    priority = Column(Text, nullable=True)
    complaint_category = Column(Text, nullable=True)

    suggested_next_action = Column(Text, nullable=True)
    initial_risk_assessment = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )