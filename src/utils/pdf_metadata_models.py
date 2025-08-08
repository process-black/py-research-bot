"""Pydantic models for structured PDF metadata extraction."""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class PDFMetadata(BaseModel):
    """Structured model for PDF metadata extraction."""
    
    title: str = Field(
        description="The title of the PDF document"
    )
    
    year: Optional[int] = Field(
        default=None,
        description="Publication year of the document (if available)",
        ge=1900,
        le=2030
    )
    
    topic: Literal[
        "Learning outcomes",
        "Tool development", 
        "Professional practice",
        "Student perspectives",
        "User experience and interaction",
        "Theoretical background",
        "AI literacy",
        "Other"
    ] = Field(
        description="Primary research topic category"
    )
    
    study_type: Literal[
        "Review",
        "Experimental", 
        "Quantitative",
        "Qualitative",
        "Mixed-methods",
        "Observational"
    ] = Field(
        description="Type of research study methodology"
    )
    
    link: Optional[str] = Field(
        default=None,
        description="URL or DOI link to the original document (if mentioned in the PDF)"
    )
    
    summary: str = Field(
        description="A comprehensive summary of the document's key findings and contributions"
    )