import os
import mimetypes
from PyPDF2 import PdfMerger

pdf_folder = r"/Users/AH0514/OneDrive - Mubea/Documents/PowerAutomatePDFs"
merged_pdf_path = r"/Users/AH0514/OneDrive - Mubea/Documents/PowerAutomatePDFs/MergedOutput.pdf"

# Get list of PDF files in the folder
pdf_files = [f for f in os.listdir(pdf_folder)
             if mimetypes.guess_type(os.path.join(pdf_folder, f))[0] == 'application/pdf']
pdf_files.sort(key=lambda x: os.path.getctime(os.path.join(pdf_folder, x)))

# Initialize the merger
merger = PdfMerger()

# Append all PDFs
for pdf in pdf_files:
    merger.append(os.path.join(pdf_folder, pdf))

# Write out the merged PDF
merger.write(merged_pdf_path)
merger.close()

print(f"Merged PDF saved at: {merged_pdf_path}")
