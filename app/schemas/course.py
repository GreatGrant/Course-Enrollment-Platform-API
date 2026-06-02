from pydantic import BaseModel, ConfigDict, Field


class CourseBase(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    code: str = Field(min_length=2, max_length=50)
    capacity: int = Field(gt=0)


class CourseCreate(CourseBase):
    is_active: bool = True


class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    code: str | None = Field(default=None, min_length=2, max_length=50)
    capacity: int | None = Field(default=None, gt=0)
    is_active: bool | None = None


class CourseStatusUpdate(BaseModel):
    is_active: bool


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    code: str
    capacity: int
    is_active: bool