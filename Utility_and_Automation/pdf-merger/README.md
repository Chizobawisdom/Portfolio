This project is a lightweight automation script designed to 'merge multiple PDF files' inside a folder into a single consolidated PDF.  
It uses Python’s built-in file handling and the `PyPDF2` library to streamline documentation workflows.

This type of tool is especially useful for:
- Quality documentation (PPAP, FAI, CAPA packages)
- Audit preparation
- Engineering reports
- Power Automate / automated documentation pipelines
- Office or administrative workflows

---

What This Script Does

- Scans a target folder for PDF files  
- Uses MIME type detection to ensure only real PDFs are included  
- Sorts files by 'creation time'  
- Appends them to a single `PdfMerger()` instance  
- Outputs a merged PDF in the same directory  

'No manual file selection needed — completely automated.'

