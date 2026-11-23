
from langchain_google_genai import ChatGoogleGenerativeAI

from security import (
    validate_question,
    build_safe_prompt,
    detect_prompt_injection
)


def extract_answer(response):
    """
    Extract only readable text from Gemini response.
    Excludes metadata such as extras and signatures.
    """

    content = response.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):

                if item.get("type") == "text":
                    text_parts.append(
                        item.get("text", "")
                    )

        return "\n".join(
            part for part in text_parts if part
        )

    if isinstance(content, dict):

        if content.get("type") == "text":
            return content.get("text", "")

    return str(content)


def get_answer(vector_store, question):

    # Validate user question
    valid, message = validate_question(question)

    if not valid:
        return {
            "answer": message,
            "sources": [],
            "warnings": []
        }

    # Retrieve relevant document chunks
    retrieved_docs = vector_store.similarity_search(
        question,
        k=5
    )

    if not retrieved_docs:
        return {
            "answer": "Answer not available in the uploaded documents.",
            "sources": [],
            "warnings": []
        }

    context_parts = []
    sources = []
    warnings = []

    for index, doc in enumerate(
        retrieved_docs, start=1
    ):

        source_id = f"S{index}"

        metadata = doc.metadata

        source_name = metadata.get(
            "source", "Unknown document"
        )

        location = []

        if "page" in metadata:
            location.append(
                f"Page {metadata['page']}"
            )

        if "sheet" in metadata:
            location.append(
                f"Sheet {metadata['sheet']}"
            )

        if "row" in metadata:
            location.append(
                f"Row {metadata['row']}"
            )

        if "paragraph" in metadata:
            location.append(
                f"Paragraph {metadata['paragraph']}"
            )

        if "table" in metadata:
            location.append(
                f"Table {metadata['table']}"
            )

        location_text = ", ".join(location)

        # Detect prompt injection
        injection_result = detect_prompt_injection(
            doc.page_content
        )

        if injection_result["is_suspicious"]:
            warnings.append(
                f"Potential prompt injection detected in "
                f"{source_name} ({source_id})."
            )

        context_parts.append(
            f"""
SOURCE ID: {source_id}
DOCUMENT: {source_name}
LOCATION: {location_text}

DOCUMENT CONTENT:
{doc.page_content}
"""
        )

        sources.append({
            "id": source_id,
            "document": source_name,
            "location": location_text,
            "content": doc.page_content
        })

    context = "\n\n".join(context_parts)

    # Construct security-aware prompt
    prompt = build_safe_prompt(
        question,
        context
    )

    # Initialize Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0
    )

    # Generate answer
    response = llm.invoke(prompt)

    # Extract clean text only
    answer = extract_answer(response)

    return {
        "answer": answer,
        "sources": sources,
        "warnings": warnings
    }
