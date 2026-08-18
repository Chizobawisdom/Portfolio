import pypdf
import os

# Function to list all pdfs in a directory
directory = "data" 

def list_pdfs_in_directory(directory):
    pdf_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            pdf_files.append(filename)
    return pdf_files

if __name__ == "__main__":
    pdf_files = list_pdfs_in_directory(directory)
    print("PDF files in directory:", pdf_files)
