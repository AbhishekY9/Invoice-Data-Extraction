
# Invoice Data Extraction and Accuracy Calculation

This project extracts key invoice data from image and PDF files, analyzes the accuracy of the extracted data, and calculates the percentage of fields successfully retrieved. The script processes files in a specified directory and computes how many fields are marked as "Not found" during the extraction process.



## Table of Contents
1. Features

2. Requirements

3. Installation

4. Usage

5. Explanation
## Features

Extracts key invoice fields from both PDF and image files (e.g., JPG, PNG).

Handles various invoice formats using OCR for images and PDF text 
extraction.

Calculates accuracy based on the number of fields successfully extracted vs. those marked as "Not found."

Processes all files in a given directory and reports accuracy per file and overall.


## Requirements

To run this script, you need the following dependencies installed:

* pytesseract (for Optical Character Recognition)

* Pillow (for image processing)

* pdfplumber (for PDF text extraction)

* Tesseract-OCR software (for image text extraction)

* re (for regular expressions, part of the Python standard library)
## Python Libraries

Install the required libraries using pip:

    pip install pytesseract pdfplumber Pillow

Tesseract Installation:

* Windows: Download and install Tesseract-OCR
* Add the Tesseract-OCR path to your system environment variables. For example:
    
      C:\Program Files\Tesseract-OCR\tesseract.exe



## Installation

* Clone or download this repository.

* Ensure that all required dependencies are installed (see the Requirements section).


## Usage

1. Place the script in a directory.

2. Ensure the files (invoices in PDF or image formats) are located in the desired directory.

3. Set the path to the directory in the script, e.g.,
           
        directory_path = r"C:\Users\lenovo\Downloads\Jan to Mar-20241016T063925Z-001\Jan to Mar"

4. Run the script:

        python invoice_extraction.py
5. The script will process each file in the directory, extract the relevant invoice data, and calculate the accuracy based on the number of "Not found" fields.

#### Output Example:
Processed file: INV-001.pdf 
        
    Not found fields: 2 out of 12
    
    Accuracy for this file: 83.33%

Processed file: INV-002.jpg

    Not found fields: 4 out of 12

    Accuracy for this file: 66.67%

Summary:

    Total files processed: 10

    Overall accuracy: 75.00%
    
    Average 'Not found' fields per file: 3.20

## Explanation of Accuracy Calculation

For each file, 12 key fields are extracted:

* Company Name

* GSTIN

* Phone Number

* Email Address

* Invoice Number

* Invoice Date

* Due Date

* Customer Name

* Place of Supply

* Total Amount

* Bank Name

* Account Number

The script counts how many of these fields are extracted successfully vs. how many are marked as "Not found". The accuracy per file is calculated as:

    Accuracy per file = ((Total fields - Not found fields) / Total fields) * 100

The overall accuracy is the average of all individual file accuracies.

## Screenshots
Here are some screenshots of the code execution:

1. ![Screenshot of executed code - Image 1](fig/image1.jpg)
2. ![Screenshot of executed code - Image 2](fig/image2.jpg)
