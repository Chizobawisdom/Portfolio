import pypdf
import os


directory = "/Users/chizobawisdom/Portfolio/Utility_and_Automation/pdf-rag-bot/data" 
# Function to list all pdfs in a directory
def list_pdfs_in_directory(directory):
    pdf_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            pdf_files.append(filename)
    return pdf_files

# Function to extract all pdfs in a directory
def extract_all_pdfs(directory):
    all_pages = []
    pdf_files = list_pdfs_in_directory(directory)
    for filename in pdf_files:
        pdf_path = os.path.join(directory, filename)
        try:
            pages = extract_text_from_pdf(pdf_path)
            all_pages.extend(pages)
        except Exception as e:
            print(f"Error occurred while processing {filename}: {e}")
    return all_pages

# Function to extract text from a pdf file
def extract_text_from_pdf(pdf_path):
    pages = []
    with open(pdf_path, 'rb') as p_file:
        reader = pypdf.PdfReader(p_file)
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if not text:
                continue
            pages.append({
                'filename': os.path.basename(pdf_path),
                'page_number': page_num,
                'text': text
            })
    return pages

if __name__ == "__main__":
    all_pages = extract_all_pdfs(directory)
    print(f"Total pages extracted: {len(all_pages)}")
    if all_pages:
        first = all_pages[0]
        print(f"First page — {first['filename']}, page {first['page_number']}:")
        print(first['text'][:200])