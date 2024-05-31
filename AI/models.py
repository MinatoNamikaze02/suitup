from typing import List, Optional

from langchain_core.pydantic_v1 import BaseModel

class Education(BaseModel):
    """Education details."""
    degree: Optional[str]
    major: Optional[str]
    institution: Optional[str]
    graduation_year: Optional[str]

class Experience(BaseModel):
    """Experience details."""
    title: Optional[str]
    company: Optional[str]
    location: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    description: Optional[str]

class Certifications(BaseModel):
    """Certifications details."""
    name: Optional[str]
    institution: Optional[str]
    date: Optional[str]

class Projects(BaseModel):
    """Projects details."""
    name: Optional[str]
    description: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    link: Optional[str]

class Resume(BaseModel):
    """Resume details."""
    name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    education: Optional[List[Education]]
    experience: Optional[List[Experience]]
    projects: Optional[List[Projects]]
    skills: Optional[str]
    languages: Optional[str]
    certifications: Optional[List[Certifications]]
    summary: Optional[str]
    additional_info: Optional[str] 
