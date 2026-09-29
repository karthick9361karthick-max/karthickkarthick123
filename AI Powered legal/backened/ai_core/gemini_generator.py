import os
import re

from dotenv import load_dotenv


load_dotenv()


class GeminiDocumentGenerator:

    def __init__(self):

        self.api_key = os.getenv(
            "GEMINI_API_KEY",
            "",
        ).strip()

        self.model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-1.5-pro",
        ).strip()

        self.demo_mode = (
            os.getenv(
                "ALLOW_DEMO_MODE",
                "true",
            ).lower()
            == "true"
        )

        self.model = None

        if self.api_key:

            try:

                import google.generativeai as genai

                genai.configure(
                    api_key=self.api_key
                )

                self.model = (
                    genai.GenerativeModel(
                        self.model_name
                    )
                )

            except Exception:

                self.model = None

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str = "",
        jurisdiction: str = "",
        language: str = "English",
    ) -> str:

        prompt = self._build_prompt(
            document_type,
            parties,
            terms,
            effective_date,
            jurisdiction,
            language,
        )

        if self.model is not None:

            response = self.model.generate_content(
                prompt
            )

            text = getattr(
                response,
                "text",
                "",
            ) or ""

            text = self._clean(text)

            if text:
                return text

        if self.demo_mode:

            return self._demo_document(
                document_type,
                parties,
                terms,
                effective_date,
                jurisdiction,
                language,
            )

        raise RuntimeError(
            "Gemini is not configured. "
            "Add GEMINI_API_KEY to .env or "
            "set ALLOW_DEMO_MODE=true."
        )

    @staticmethod
    def _build_prompt(
        document_type,
        parties,
        terms,
        effective_date,
        jurisdiction,
        language,
    ):

        return f"""
You are a careful legal drafting assistant.

Create a professional {document_type}.

PARTIES:
{parties}

TERMS AND CONDITIONS:
{terms}

EFFECTIVE DATE:
{effective_date or "Not specified"}

JURISDICTION:
{jurisdiction or "Not specified"}

LANGUAGE:
{language}

Requirements:

1. Do not invent names, amounts, dates,
   addresses, laws, or obligations.

2. Use [TO BE COMPLETED] when required
   information is missing.

3. Use clear legal headings.

4. Use numbered clauses.

5. Preserve every material user-provided term.

6. Include signature blocks where appropriate.

7. Do not add explanations about the
   generation process.

8. Produce only the legal document.

9. Clearly treat the result as a draft.
"""

    @staticmethod
    def _clean(text: str) -> str:

        text = re.sub(
            r"```(?:text|markdown)?",
            "",
            text,
            flags=re.I,
        )

        text = text.replace(
            "```",
            "",
        )

        return text.strip()

    @staticmethod
    def _demo_document(
        document_type,
        parties,
        terms,
        effective_date,
        jurisdiction,
        language,
    ):

        term_items = [
            item.strip(" -•\t")
            for item in re.split(
                r";|\n",
                terms,
            )
            if item.strip()
        ]

        terms_block = "\n".join(
            f"{index}. {item}"
            for index, item
            in enumerate(
                term_items,
                start=1,
            )
        )

        return f"""
DRAFT {document_type.upper()}

IMPORTANT NOTICE

This document is an AI-assisted draft
for review. It is not a substitute for
advice from a qualified legal professional.

1. PARTIES

{parties}

2. EFFECTIVE DATE

{effective_date or "[TO BE COMPLETED]"}

3. PURPOSE AND SCOPE

The parties intend to enter into this
{document_type}. The rights and obligations
are based on the information supplied by
the user.

4. TERMS AND CONDITIONS

{terms_block or "1. [TO BE COMPLETED]"}

5. JURISDICTION

{jurisdiction or "[TO BE COMPLETED]"}

6. GENERAL

Any material information not supplied above
should be completed and reviewed before
execution.

7. SIGNATURES

Party 1: ______________________________

Name: __________________________________

Date: ___________________________________

Party 2: ______________________________

Name: __________________________________

Date: ___________________________________
"""