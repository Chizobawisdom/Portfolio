---
# End-to-End TensorFlow PDF Data Preprocessing Pipeline for NLP
---

This project presents an end-to-end data preprocessing pipeline for PDF
documents using TensorFlow. The pipeline is designed to efficiently parse,
clean, and prepare textual content from PDF files for downstream Natural
Language Processing (NLP) tasks.

The workflow integrates TensorFlow’s tf.data API for scalable data handling,
PyPDF2 for PDF document parsing, and the NLTK library for linguistic text
cleaning, including tokenization and stopword removal.

The final output of the pipeline is a set of cleaned text tokens that are
directly suitable for use in modern NLP models.

---

The main objectives of this project are:

- To demonstrate document-level and page-level text extraction from PDFs
- To implement an efficient TensorFlow-based preprocessing pipeline
- To apply NLP-specific text cleaning using the NLTK library
- To demonstrate parallel processing of textual data using tf.data
- To generate NLP-ready tokens for machine learning models

---

Applications:
 - Text Classification
 - Topic Modeling
 - Information Retrieval
 - Word Embedding Training
 - Transformer-Based Models