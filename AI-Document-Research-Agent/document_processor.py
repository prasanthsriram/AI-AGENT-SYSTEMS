
import io
import pandas as pd

from pypdf import PdfReader
from docx import Document as WordDocument
from langchain_core.documents import Document


def process_pdf(file):
    documents = []

    pdf = PdfReader(io.BytesIO(file.getvalue()))

    for page_number, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": file.name,
                        "file_type": "PDF",
                        "page": page_number
                    }
                )
            )

    return documents  


def process_docx(file):
    documents = []

    word_file = WordDocument(io.BytesIO(file.getvalue()))

    for index, paragraph in enumerate(
        word_file.paragraphs, start=1
    ):
        text = paragraph.text.strip()

        if text:
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": file.name,
                        "file_type": "DOCX",
                        "paragraph": index
                    }
                )
            )

    # Process tables as well
    for table_index, table in enumerate(
        word_file.tables, start=1
    ):
        for row_index, row in enumerate(
            table.rows, start=1
        ):
            text = " | ".join(
                cell.text.strip() for cell in row.cells
            )

            if text.strip():
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": file.name,
                            "file_type": "DOCX",
                            "table": table_index,
                            "row": row_index
                        }
                    )
                )

    return documents


def process_excel(file):
    documents = []

    excel = pd.ExcelFile(io.BytesIO(file.getvalue()))

    for sheet_name in excel.sheet_names:

        df = pd.read_excel(
            excel,
            sheet_name=sheet_name
        )

        df = df.fillna("")

        for row_index, row in df.iterrows():

            row_content = " | ".join(
                f"{column}: {value}"
                for column, value in row.items()
                if str(value).strip()
            )

            if row_content.strip():
                documents.append(
                    Document(
                        page_content=row_content,
                        metadata={
                            "source": file.name,
                            "file_type": "XLSX",
                            "sheet": sheet_name,
                            "row": int(row_index) + 2
                        }
                    )
                )

    return documents


def process_txt(file):
    text = file.getvalue().decode(
        "utf-8",
        errors="replace"
    )

    return [
        Document(
            page_content=text,
            metadata={
                "source": file.name,
                "file_type": "TXT"
            }
        )
    ]


def process_uploaded_file(file):

    extension = file.name.lower().split(".")[-1]

    if extension == "pdf":
        return process_pdf(file)

    elif extension == "docx":
        return process_docx(file)

    elif extension in ["xlsx", "xlsm"]:
        return process_excel(file)

    elif extension == "txt":
        return process_txt(file)

    else:
        raise ValueError(
            f"Unsupported file format: {extension}"
        )
