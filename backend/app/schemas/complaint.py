from pydantic import BaseModel


class ComplaintData(BaseModel):
    complaint_source: str | None = None
    customer_name: str | None = None

    product_name: str | None = None
    product_strength: str | None = None

    batch_number: str | None = None
    manufacturing_date: str | None = None
    expiry_date: str | None = None

    affected_quantity: str | None = None

    complaint_type: str | None = None
    complaint_description: str | None = None

    severity: str | None = None
    priority: str | None = None
    complaint_category: str | None = None

    suggested_next_action: str | None = None
    initial_risk_assessment: str | None = None


class ComplaintResponse(ComplaintData):
    id: int

    class Config:
        from_attributes = True