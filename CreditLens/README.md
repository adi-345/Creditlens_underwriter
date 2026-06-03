# CreditLens: Autonomous AI Underwriting Agent

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge)](YOUR_CREDITLENS_URL_HERE)

CreditLens is a Retrieval-Augmented Generation (RAG) pipeline and full-stack web application built as a project. It automates the extraction and analysis of financial data from massive corporate Annual Reports, generating deterministic risk assessments in seconds.

## Features
* **Intelligent Ingestion:** Utilizes PyMuPDF to parse dense, 300+ page financial statements.
* **Deterministic RAG Extraction:** Leverages Llama 3.3 (70B) via the Groq API to extract specific accounting line items with a strict `temperature=0` constraint to eliminate hallucination.
* **Algorithmic Risk Engine:** Calculates standard banker ratios (Liquidity, Leverage, Profitability, Growth) to generate a weighted 0-100 Confidence Score.
* **Full-Stack Architecture:** Decoupled FastAPI backend and Streamlit frontend.

## Tech Stack
* **Backend:** Python, FastAPI, Uvicorn
* **AI/LLM:** Groq API (Llama-3.3-70b-versatile)
* **Document Parsing:** PyMuPDF (fitz)
* **Frontend:** Streamlit, Requests

## Local Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Set your Groq API key: `set GROQ_API_KEY=your_key_here` (Windows).
4. Run the API: `uvicorn api:app --reload`
5. Run the Frontend: `streamlit run app.py`