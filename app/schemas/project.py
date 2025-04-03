from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# -------------------------------
# 📌 Project Schema
# -------------------------------
class Project(BaseModel):
    project_id: str = Field(..., description="Unique identifier for the project")
    name: str
    description: str
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str  # e.g., "Planned", "In Progress", "Completed"
    department_id: str
    budget_id: str
    stakeholders: List[str] = []  # List of stakeholder IDs

# -------------------------------
# 📌 Stakeholder Schema
# -------------------------------
class Stakeholder(BaseModel):
    stakeholder_id: str
    name: str
    role: str  # e.g., "Sponsor", "Team Member", "Government Official"
    contact_email: Optional[str] = None
    phone_number: Optional[str] = None
    project_id: str  # Links stakeholder to a project

# -------------------------------
# 📌 Risk Management Schema
# -------------------------------
class Risk(BaseModel):
    risk_id: str
    project_id: str
    description: str
    impact_level: str  # "Low", "Medium", "High"
    likelihood: str  # "Rare", "Unlikely", "Possible", "Likely", "Certain"
    mitigation_plan: Optional[str] = None
    owner: Optional[str] = None  # Stakeholder responsible

# -------------------------------
# 📌 Issue Tracking Schema
# -------------------------------
class Issue(BaseModel):
    issue_id: str
    project_id: str
    description: str
    severity: str  # "Low", "Medium", "High", "Critical"
    reported_by: str  # Stakeholder ID
    status: str  # "Open", "Resolved", "Closed"
    resolution: Optional[str] = None

# -------------------------------
# 📌 Budget Management Schema
# -------------------------------
class Budget(BaseModel):
    budget_id: str
    project_id: str
    total_amount: float
    allocated_amount: float
    spent_amount: float
    remaining_amount: float = Field(..., description="Total - Spent")
    last_updated: datetime

# -------------------------------
# 📌 Task Management Schema
# -------------------------------
class Task(BaseModel):
    task_id: str
    project_id: str
    name: str
    assigned_to: str  # Stakeholder ID
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str  # "Pending", "In Progress", "Completed"

# -------------------------------
# 📌 Benefits Realization Schema
# -------------------------------
class Benefit(BaseModel):
    benefit_id: str
    project_id: str
    description: str
    expected_outcome: str
    actual_outcome: Optional[str] = None
    realization_date: Optional[datetime] = None

# -------------------------------
# 📌 Quality Management Schema
# -------------------------------
class QualityControl(BaseModel):
    quality_id: str
    project_id: str
    metric: str  # E.g., "Defect Rate", "Customer Satisfaction"
    target_value: float
    actual_value: Optional[float] = None
    status: str  # "Met", "Not Met", "Exceeded"

# -------------------------------
# 📌 Generic Insert Schema for Any Collection
# -------------------------------
class InsertData(BaseModel):
    collection_name: str
    data: Dict[str, Any]
