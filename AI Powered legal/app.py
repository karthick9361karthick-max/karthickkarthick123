import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        color: #6b7280;
        margin-top: 0.2rem;
    }

    .preview {
        background: #111827;
        color: #f9fafb;
        padding: 28px;
        border-radius: 14px;
        min-height: 420px;
        max-height: 650px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: Georgia, serif;
        line-height: 1.7;
    }

    .small-note {
        color: #6b7280;
        font-size: .9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered legal document drafting and export'
    '</div>',
    unsafe_allow_html=True,
)

with st.sidebar:

    st.header("Document details")

    document_type = st.selectbox(
        "Document type",
        [
            "Agreement",
            "Contract",
            "NDA (Non-Disclosure Agreement)",
            "Lease Agreement",
            "Employment Contract",
            "Employment Offer Letter",
            "Freelance Work Contract",
            "Service Agreement",
            "Custom",
        ],
    )

    if document_type == "Custom":
        document_type = st.text_input(
            "Custom document type",
            "Legal Agreement",
        )

    parties = st.text_area(
        "Parties involved",
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=110,
    )

    terms = st.text_area(
        "Terms & conditions",
        placeholder=(
            "Payment to be made within 30 days of invoice;\n"
            "Confidentiality must be maintained;\n"
            "Either party may terminate with 15 days notice"
        ),
        height=180,
    )

    effective_date = st.text_input(
        "Effective date",
        placeholder="April 15, 2026",
    )

    jurisdiction = st.text_input(
        "Jurisdiction (optional)",
        placeholder="Tamil Nadu, India",
    )

    language = st.selectbox(
        "Output language",
        ["English", "Tamil", "Hindi"],
    )

    generate = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True,
    )


if "document" not in st.session_state:
    st.session_state.document = ""

if "last_request" not in st.session_state:
    st.session_state.last_request = None


if generate:

    if not parties.strip():
        st.error("Please enter the parties involved.")

    elif not terms.strip():
        st.error("Please enter at least one term or condition.")

    else:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date,
            "jurisdiction": jurisdiction,
            "language": language,
        }

        try:

            with st.spinner(
                "Generating your legal document..."
            ):

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=180,
                )

            if response.ok:

                data = response.json()

                st.session_state.document = data["document"]
                st.session_state.last_request = payload

                st.success(
                    "Document generated successfully."
                )

            else:

                try:
                    detail = response.json().get(
                        "detail",
                        response.text,
                    )
                except Exception:
                    detail = response.text

                st.error(
                    f"Backend error: {detail}"
                )

        except requests.RequestException as exc:

            st.error(
                "Could not connect to FastAPI. "
                "Start the backend with "
                "`uvicorn backend.main:app --reload --port 8000`."
            )

            st.caption(str(exc))


st.subheader("Document preview")


if st.session_state.document:

    edited = st.text_area(
        "Editable document",
        value=st.session_state.document,
        height=560,
        key="editable_document",
    )

    st.session_state.document = edited

    col1, col2, col3 = st.columns(3)

    request_data = (
        st.session_state.last_request or {}
    )

    doc_type_for_export = request_data.get(
        "document_type",
        "Legal Document",
    )

    with col1:

        st.download_button(
            "⬇️ Download TXT",
            data=st.session_state.document.encode(
                "utf-8"
            ),
            file_name="legalese_document.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with col2:

        try:

            response = requests.post(
                f"{BACKEND_URL}/export/docx",
                json={
                    "text": st.session_state.document,
                    "document_type": doc_type_for_export,
                },
                timeout=60,
            )

            if response.ok:

                st.download_button(
                    "⬇️ Download DOCX",
                    data=response.content,
                    file_name="legalese_document.docx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),
                    use_container_width=True,
                )

            else:
                st.error("DOCX export failed.")

        except requests.RequestException:
            st.error(
                "Backend unavailable for DOCX export."
            )

    with col3:

        try:

            response = requests.post(
                f"{BACKEND_URL}/export/pdf",
                json={
                    "text": st.session_state.document,
                    "document_type": doc_type_for_export,
                },
                timeout=60,
            )

            if response.ok:

                st.download_button(
                    "⬇️ Download PDF",
                    data=response.content,
                    file_name="legalese_document.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            else:
                st.error("PDF export failed.")

        except requests.RequestException:
            st.error(
                "Backend unavailable for PDF export."
            )

    st.markdown("#### Formatted preview")

    preview_response = None

    try:

        preview_response = requests.post(
            f"{BACKEND_URL}/preview",
            json={
                "text": st.session_state.document
            },
            timeout=30,
        )

    except requests.RequestException:
        pass

    if preview_response is not None and preview_response.ok:

        st.markdown(
            f'<div class="preview">'
            f'{preview_response.json()["html"]}'
            f'</div>',
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            f'<div class="preview">'
            f'{st.session_state.document}'
            f'</div>',
            unsafe_allow_html=True,
        )

else:

    st.info(
        "Enter the document details in the sidebar "
        "and click Generate Document."
    )

    st.markdown(
        '<div class="small-note">'
        'LegalEase provides drafting assistance. '
        'Review generated content with a qualified '
        'legal professional before relying on it.'
        '</div>',
        unsafe_allow_html=True,
    )