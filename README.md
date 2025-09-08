AI-Based Resume Screening System

This project is an AI-powered application designed to streamline the recruitment process by automatically screening and ranking resumes based on job descriptions. The system leverages natural language processing (NLP) to analyze candidate information, making the hiring process more efficient and objective.

1. Features:- 

1. Resume Parsing: Extracts key information from resumes (e.g., skills, experience, education).

2. Job Description Analysis: Understands and tokenizes the requirements of a job.

3. AI-Powered Matching: Uses machine learning models to score and rank resumes against a specific job description.

4. User-Friendly Dashboard: A clean frontend for recruiters to upload resumes, input job descriptions, and view results.

2. Technology Stack

Frontend

HTML: For the structure of the web pages.

CSS: For styling and layout.

JavaScript: For dynamic interactions and API calls to the backend.

Backend

Python: The core language for the backend logic.

Flask: A micro web framework used for the main application and handling web requests.

FastAPI: A modern, fast web framework used for a specific, high-performance API endpoint (e.g., the ML model's inference endpoint). This allows for a blended approach, leveraging the strengths of both frameworks.

Scikit-learn/Spacy/NLTK: Libraries for the NLP and machine learning components.

AI Models
 
The system's intelligence is powered by two state-of-the-art transformer models:

1. BERT (Bidirectional Encoder Representations from Transformers):

Function: BERT is an encoder-only model that excels at text understanding. We use a fine-tuned version of BERT (or a variant like S-BERT) to perform semantic matching.

How it works:

Both the resume text and the job description text are converted into numerical representations (embeddings) using the BERT model.

These embeddings capture the contextual meaning of the text.

The system then calculates the cosine similarity between the job description embedding and each resume embedding.

A higher similarity score indicates a better match, allowing the system to rank candidates accurately based on their relevance.

2. T5 (Text-to-Text Transfer Transformer):

Function: T5 is an encoder-decoder model that is excellent for text generation tasks. We use a fine-tuned T5 model for resume summarization.

How it works:

The complete resume text is fed into the T5 model.

The model is trained on a text-to-text task to generate a summary. For example, it takes the input summarize: [resume_text] and outputs a short, coherent summary.

This feature provides a quick overview of a candidate, saving time for recruiters.
