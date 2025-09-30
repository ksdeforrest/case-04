from datetime import datetime
from typing import Optional
import hashlib
from pydantic import BaseModel, Field, EmailStr, validator

class SurveySubmission(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=13, le=120)
    consent: bool = Field(..., description="Must be true to accept")
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    user_agent: Optional[str] = Field(None, description="Browser or client identifier")
    submission_id: Optional[str] = Field(None, description="Unique submission identifier")
  

    @validator("comments")
    def _strip_comments(cls, v):
        return v.strip() if isinstance(v, str) else v

    @validator("consent")
    def _must_consent(cls, v):
        if v is not True:
            raise ValueError("consent must be true")
        return v
    
    @validator("submission_id", always=True)
    def _generate_submission_id(cls, v, values):
        """Generate submission_id if not provided"""
        if v is None:
            email = values.get('email')
            if email:
                # Generate hash from email + current date and hour
                now = datetime.now()
                date_hour = now.strftime("%Y%m%d%H")
                hash_input = f"{email}{date_hour}"
                return hashlib.sha256(hash_input.encode()).hexdigest()
        return v
    
    def get_hashed_email(self) -> str:
        """Return SHA-256 hash of email"""
        return hashlib.sha256(self.email.encode()).hexdigest()
    
    def get_hashed_age(self) -> str:
        """Return SHA-256 hash of age"""
        return hashlib.sha256(str(self.age).encode()).hexdigest()
        
#Good example of inheritance
class StoredSurveyRecord(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    consent: bool = Field(..., description="Must be true to accept")
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    user_agent: Optional[str] = Field(None, description="Browser or client identifier")
    submission_id: Optional[str] = Field(None, description="Unique submission identifier")
    received_at: datetime
    ip: str
    hashed_email: str  # SHA-256 hash of email
    hashed_age: str    # SHA-256 hash of age
    
    @validator("comments")
    def _strip_comments(cls, v):
        return v.strip() if isinstance(v, str) else v

    @validator("consent")
    def _must_consent(cls, v):
        if v is not True:
            raise ValueError("consent must be true")
        return v
    
    @validator("submission_id", always=True)
    def _generate_submission_id(cls, v, values):
        """Generate submission_id if not provided"""
        if v is None:
            # We need to reconstruct the email from the submission data
            # This is a bit tricky since we don't have the original email here
            # For now, we'll skip auto-generation in StoredSurveyRecord
            pass
        return v
    
    @classmethod
    def from_submission(cls, submission: SurveySubmission, received_at: datetime, ip: str):
        """Create a StoredSurveyRecord from a SurveySubmission, automatically hashing PII"""
        return cls(
            name=submission.name,
            consent=submission.consent,
            rating=submission.rating,
            comments=submission.comments,
            user_agent=submission.user_agent,
            submission_id=submission.submission_id,
            received_at=received_at,
            ip=ip,
            hashed_email=submission.get_hashed_email(),
            hashed_age=submission.get_hashed_age()
        )
