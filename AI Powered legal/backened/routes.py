from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.ai_core.gemini_generator import (
    GeminiDocumentGenerator,
)

from backend.schemas import (
    DocumentRequest,
    ExportRequest,
    PreviewRequest,
)

from backend.services.document_service import (
    format_docx,
    format_pdf,
    format_html_preview,
)


router = APIRouter()

generator = GeminiDocumentGenerator()


@router.post("/generate")
def generate_document(
    request: DocumentRequest,
):

    try:

        text = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
            jurisdiction=request.jurisdiction,
            language=request.language,
        )

        return {
            "document": text,
            "document_type": request.document_type,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/preview")
def preview_document(
    request: PreviewRequest,
):

    return {
        "html": format_html_preview(
            request.text
        )
    }


@router.post("/export/docx")
def export_docx(
    request: ExportRequest,
):

    try:

        content = format_docx(
            request.text,
            request.document_type,
        )

        return Response(
            content=content,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            headers={
                "Content-Disposition":
                'attachment; filename="legalese_document.docx"'
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/export/pdf")
def export_pdf(
    request: ExportRequest,
):

    try:

        content = format_pdf(
            request.text,
            request.document_type,
        )

        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                'attachment; filename="legalese_document.pdf"'
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )