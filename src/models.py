"""
Data models for the Terraform Plan Analyzer.
"""
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ErrorType(str, Enum):
    """Types of errors that can be found in Terraform plans."""
    VALIDATION = "validation"
    DEPENDENCY = "dependency"
    PERMISSION = "permission"
    SYNTAX = "syntax"
    RESOURCE_CONFLICT = "resource_conflict"
    STATE_MISMATCH = "state_mismatch"
    PROVIDER = "provider"
    MODULE = "module"
    OTHER = "other"


class ConfidenceLevel(str, Enum):
    """Confidence levels for recommendations."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ResponseStatus(str, Enum):
    """Overall status of the analysis."""
    SUCCESS = "success"
    ERROR = "error"
    UNKNOWN = "unknown"


class AffectedResource(BaseModel):
    """Model representing a resource affected by an error."""
    name: str = Field(..., description="Resource name")
    type: str = Field(..., description="Resource type (e.g., aws_instance)")
    address: str = Field(..., description="Full resource address in Terraform")


class Recommendation(BaseModel):
    """Model representing a solution recommendation."""
    description: str = Field(..., description="Friendly explanation of solution")
    code: Optional[str] = Field(None, description="Example code or command to fix the issue")
    confidence: ConfidenceLevel = Field(..., description="Confidence level in the recommendation")


class Error(BaseModel):
    """Model representing an error found in the Terraform plan."""
    errorType: ErrorType = Field(..., description="Type of error detected")
    message: str = Field(..., description="Human-friendly error explanation")
    affectedResources: List[AffectedResource] = Field(default_factory=list, 
                                                     description="Resources affected by this error")
    recommendations: List[Recommendation] = Field(default_factory=list, 
                                                 description="Recommendations to fix this error")


class ResourceCounts(BaseModel):
    """Model representing resource counts in the plan."""
    add: int = Field(0, description="Number of resources to add")
    change: int = Field(0, description="Number of resources to change")
    destroy: int = Field(0, description="Number of resources to destroy")


class Metadata(BaseModel):
    """Model representing metadata about the analysis."""
    planId: Optional[str] = Field(None, description="Optional plan identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of analysis")
    resourceCount: Optional[ResourceCounts] = Field(None, 
                                                  description="Count of resources by operation")


class AnalysisResponse(BaseModel):
    """Model representing the full analysis response."""
    status: ResponseStatus = Field(..., description="Overall status of the analysis")
    summary: str = Field(..., description="Friendly overview of plan results")
    errors: List[Error] = Field(default_factory=list, description="List of errors found in the plan")
    metadata: Metadata = Field(default_factory=Metadata, description="Metadata about the analysis")