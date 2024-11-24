from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def main():
    # Test PDF extraction
    pdf_path = "docs/test.pdf"
    
    try:
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"Error: File {pdf_path} does not exist!")
            return
            
        # Extract text
        text = extract_text_from_pdf(pdf_path)
        
        # Print first 500 characters to verify content
        print("First 500 characters of extracted text:")
        print("-" * 50)
        print(text[:500])
        print("-" * 50)
        
        # Print total length
        print(f"\nTotal length of extracted text: {len(text)} characters")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
