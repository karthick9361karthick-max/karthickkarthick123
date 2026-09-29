from pydantic import BaseModel, Field


class DocumentRequest(BaseModel):

    document_type: str = Field(
        ...,
        min_length=2,
        max_length=120,
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=5000,
    )

    terms: str = Field(
        ...,
        min_length=2,
        max_length=12000,
    )

    effective_date: str = Field(
        default="",
        max_length=100,
    )

    jurisdiction: str = Field(
        default="",
        max_length=200,
    )

    language: str = Field(
        default="English",
        max_length=50,
    )


class ExportRequest(BaseModel):

    text: str = Field(
        ...,
        min_length=1,
        max_length=100000,
    )

    document_type: str = Field(
        default="Legal Document",
        max_length=120,
    )


class PreviewRequest(BaseModel):

    text: str = Field(
        ...,
        min_length=1,
        max_length=100000,
    )