import os
import json
import uuid
from typing import List, Optional, Literal
from pydantic import BaseModel, UUID4, HttpUrl, Field, ValidationError
from datetime import date
from enum import Enum


# --- Enums based on TypeScript literal types ---
class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    unknown = "unknown"

class RelationshipType(str, Enum):
    parent = "parent"
    spouse = "spouse"
    sibling = "sibling"
    child = "child"
    grandparent = "grandparent"
    grandchild = "grandchild"
    friend = "friend"
    colleague = "colleague"
    other = "other"
    father = "father" # Retained as per original, LLM should be guided by prompt
    mother = "mother" # Retained as per original, LLM should be guided by prompt


class AllergySeverity(str, Enum):
    mild = "mild"
    moderate = "moderate"
    severe = "severe"

class SmokingStatus(str, Enum):
    never = "never"
    former = "former"
    current = "current"
    unknown = "unknown"

class ThemeType(str, Enum):
    light = "light"
    dark = "dark"

# --- Pydantic Models based on TypeScript Interfaces ---

class Source(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    title: str
    url: Optional[HttpUrl] = None
    text: Optional[str] = None
    appliesToField: Optional[str] = None

class HealthCondition(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str
    diagnosisDate: Optional[date] = None
    notes: Optional[str] = None

class Allergy(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str
    severity: AllergySeverity

class Medication(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str
    dosage: Optional[str] = None
    isCurrent: bool

class VitalOrScreening(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    type: str
    value: str
    date: date

class Lifestyle(BaseModel):
    smoking: SmokingStatus = SmokingStatus.unknown
    dietNotes: Optional[str] = None
    exerciseNotes: Optional[str] = None

class CustomTimelineEvent(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    date: date
    title: Optional[str] = None
    description: str
    icon: Optional[str] = None

class FamilyMember(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4) # Will be overridden by post-processing logic
    firstName: str
    lastName: str
    maidenName: Optional[str] = None
    birthDate: Optional[date] = None
    deathDate: Optional[date] = None
    causeOfDeath: Optional[str] = None
    gender: Gender = Gender.unknown
    photoUrl: Optional[HttpUrl] = None
    birthPlace: Optional[str] = None
    deathPlace: Optional[str] = None
    occupation: Optional[str] = None
    bio: Optional[str] = None
    isPrivate: Optional[bool] = False
    conditions: List[HealthCondition] = Field(default_factory=list)
    allergies: List[Allergy] = Field(default_factory=list)
    medications: List[Medication] = Field(default_factory=list)
    lifestyle: Optional[Lifestyle] = Field(default_factory=lambda: Lifestyle(smoking=SmokingStatus.unknown))
    vitals: List[VitalOrScreening] = Field(default_factory=list)
    customTimelineEvents: List[CustomTimelineEvent] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    generation: Optional[int] = None

class Relationship(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    from_member: UUID4 = Field(alias="from")
    to_member: UUID4 = Field(alias="to")
    type: RelationshipType
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    details: Optional[str] = None

class FamilyTreeData(BaseModel):
    members: List[FamilyMember] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    theme: ThemeType = ThemeType.light
