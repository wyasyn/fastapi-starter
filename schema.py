from enum import IntEnum
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class Priority(IntEnum):
    """Priority levels for the task."""
    HIGH = 1
    MEDIUM = 2
    LOW = 3

    def __str__(self):
        return self.name.capitalize()


class TaskBase(BaseModel):
    """Base schema shared by all task operations."""
    title: str = Field(..., description="Title of the task", example="Buy groceries")
    description: Optional[str] = Field(None, description="Detailed description of the task", example="Milk, eggs, bread")
    priority: Priority = Field(Priority.LOW, description="Priority level of the task", example=Priority.MEDIUM)
    completed: bool = Field(False, description="Completion status", example=False)

    @validator("title")
    def title_min_length(cls, v):
        if len(v.strip()) <= 5:
            raise ValueError("Title must be more than 5 characters.")
        return v

    @validator("description")
    def description_min_length(cls, v):
        if v is not None and len(v.strip()) <= 10:
            raise ValueError("Description must be more than 10 characters if provided.")
        return v

    class Config:
        use_enum_values = True


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    id: Optional[int] = Field(None, description="Unique task ID", example=1)
    title: Optional[str] = Field(None, description="Updated title", example="Read a book")
    description: Optional[str] = Field(None, description="Updated description", example="Read chapters 1 to 3")
    priority: Optional[Priority] = Field(None, description="Updated priority", example=Priority.HIGH)
    completed: Optional[bool] = Field(None, description="Updated completion status", example=True)

    @validator("title")
    def title_min_length(cls, v):
        if v is not None and len(v.strip()) <= 5:
            raise ValueError("Title must be more than 5 characters if provided.")
        return v

    @validator("description")
    def description_min_length(cls, v):
        if v is not None and len(v.strip()) <= 10:
            raise ValueError("Description must be more than 10 characters if provided.")
        return v

    class Config:
        from_attributes = True
        use_enum_values = True


class Task(TaskBase):
    """Model for a task with an ID and timestamps."""
    id: int = Field(..., description="Unique identifier for the task")
    created_at: datetime = Field(..., description="Timestamp when task was created")
    updated_at: datetime = Field(..., description="Timestamp when task was last updated")

    class Config:
        from_attributes = True
        use_enum_values = True


class TaskList(BaseModel):
    tasks: List[Task] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of matching tasks")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of tasks per page")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        from_attributes = True 

