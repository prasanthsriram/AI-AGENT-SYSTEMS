AI Document Research Agent – Complete Project Guide
--------------------------------------------------
We can build this as a complete AI-powered Document Research Agent using Python, Streamlit, LangChain, FAISS, and Google Gemini.

The goal is to create an application where users can upload multiple PDF, Word, and Excel documents, ask questions in natural language, and receive answers based strictly on the uploaded documents, with source citations and prompt injection protection.

<img width="576" height="458" alt="image" src="https://github.com/user-attachments/assets/088f2590-860f-4d43-b6a1-c09858c5097e" /> <img width="567" height="408" alt="image" src="https://github.com/user-attachments/assets/9f6e80b5-f60a-4a08-8b79-b0227fef74db" />



Technology stack:
-----------------
Component	  Technology	      Purpose
Frontend	  Streamlit	        User interface
Programming	Python	          Application logic
LLM	        Gemini 2.5 Flash	Answer generation
Embedding	  Gemini Embedding	Text vectorization
Vector DB	  FAISS	            Similarity search
Framework	  LangChain	        Document and model integration
PDF	        PyPDF	            PDF extraction
Word	      python-docx      	DOCX extraction
Excel	      openpyxl / pandas	Excel extraction
Security	  Input validation  Injection mitigation
                 + 
            prompt isolation	

Python file has a specific responsibility.
----------------------------------------
File	                  Responsibility
app.py	                Streamlit user interface
document_processor.py	  Read PDF, Word, Excel files
vector_store.py	        Create and search FAISS database
security.py	            Prompt injection protection
qa_engine.py	          Gemini question-answering logic

Text splitting and FAISS:
-------------------------
Why do we need chunking?

Imagine a 100-page PDF document.

Instead of sending all 100 pages to Gemini for every question, we divide the document into smaller sections.

Example:


<img width="619" height="311" alt="image" src="https://github.com/user-attachments/assets/d994000d-0a80-4ebb-852d-efec1890a12c" />



Important: This first version handles text-based PDFs. Scanned PDFs containing only images need OCR processing. We can add OCR in a later enhancement.
