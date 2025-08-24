#!/usr/bin/env python3
"""
Create a simple test PDF for manual testing
"""
import fitz  # PyMuPDF
import os
import sys

# Add parent directory to path for imports if needed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_test_pdf(filename="test_document.pdf"):
    """Create a simple PDF with scientific content for testing"""
    
    doc = fitz.open()  # Create new PDF
    
    # Page 1
    page1 = doc.new_page()
    
    # Add some scientific text
    text1 = """
    DNA Structure and Function
    
    DNA (Deoxyribonucleic acid) is the hereditary material in humans and almost all other organisms. 
    Nearly every cell in a person's body has the same DNA. Most DNA is located in the cell nucleus, 
    but a small amount of DNA can also be found in the mitochondria.
    
    The information in DNA is stored as a code made up of four chemical bases: adenine (A), 
    guanine (G), cytosine (C), and thymine (T). Human DNA consists of about 3 billion bases, 
    and more than 99 percent of those bases are the same in all people.
    
    Protein Synthesis
    
    Proteins are large, complex molecules that play many critical roles in the body. They do most 
    of the work in cells and are required for the structure, function, and regulation of the body's 
    tissues and organs. Proteins are made up of hundreds or thousands of smaller units called amino acids.
    """
    
    # Insert text
    page1.insert_text((50, 50), text1, fontsize=11, fontname="helv")
    
    # Page 2
    page2 = doc.new_page()
    
    text2 = """
    Cell Division Process
    
    Cell division is the process by which a parent cell divides into two daughter cells. 
    Cell division usually occurs as part of a larger cell cycle. In eukaryotes, there are 
    two distinct types of cell division: mitosis and meiosis.
    
    Mitosis is used for growth and repair, while meiosis is used for sexual reproduction. 
    During mitosis, the cell duplicates its contents, including its chromosomes, and splits 
    to form two identical daughter cells.
    
    Photosynthesis
    
    Photosynthesis is the process used by plants and other organisms to convert light energy 
    into chemical energy. This process occurs in the chloroplasts of plant cells and involves 
    the conversion of carbon dioxide and water into glucose using sunlight.
    """
    
    page2.insert_text((50, 50), text2, fontsize=11, fontname="helv")
    
    # Save the PDF
    doc.save(filename)
    doc.close()
    
    print(f"Test PDF created: {filename}")
    print("This PDF contains scientific content perfect for testing the highlighter.")
    
    return filename

if __name__ == "__main__":
    create_test_pdf()