import os
import re
from PIL import Image, ImageEnhance, ImageFilter
import pdfplumber
import pytesseract


def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        lines = []
        for page in pdf.pages:
            lines.extend(page.extract_text().split("\n"))
    return lines


def preprocess_image(image_path):
    image = Image.open(image_path)
    image = image.convert("L")
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image = image.filter(ImageFilter.MedianFilter(size=3))
    image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)
    return image


def extract_text_from_image(image_path):
    processed_image = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_image)
    return text.split("\n")


def clean_text(text):
    return text.strip().replace("\n", " ").replace("\r", " ").strip()


def extract_invoice_data(lines):
    text = " ".join(lines)
    # Regex patterns for extracting invoice details
    company_name_pattern = r"((\w+\s+){3}\w+)\s+GSTIN"
    gstin_pattern = r"GSTIN\s([\dA-Z]+)"
    phone_pattern = r"Mobile\s*([+\d\s]+)"
    email_pattern = r"Email\s*([\w\.-]+@[\w\.-]+)"
    invoice_number_pattern = r"Invoice\s#:\s([A-Z0-9\-]+)"
    invoice_date_pattern = r"Invoice Date:\s([\d]+\s[A-Za-z]+\s[\d]+)"
    due_date_pattern = r"Due Date:\s([\d]+\s[A-Za-z]+\s[\d]+)"
    customer_pattern = r"Customer Details:\s([\w\s]+)(?=\sPh:|Place)"
    total_amount_pattern = r"Total\s(?:₹)?([\d,]+\.\d{2})"
    place_of_supply_pattern = r"Place of Supply:\s([\dA-Z\- ]+)"
    bank_name_pattern = r"Bank:\s([\w\s]+) Account"
    account_number_pattern = r"Account\s#:\s([\d]+)"

    # Extracting data using the regex patterns
    company_name = clean_text(re.search(company_name_pattern, text).group(1)) if re.search(company_name_pattern, text) else "Not found"
    gstin = clean_text(re.search(gstin_pattern, text).group(1)) if re.search(gstin_pattern, text) else "Not found"
    phone = clean_text(re.search(phone_pattern, text).group(1)) if re.search(phone_pattern, text) else "Not found"
    email = clean_text(re.search(email_pattern, text).group(1)) if re.search(email_pattern, text) else "Not found"
    invoice_number = clean_text(re.search(invoice_number_pattern, text).group(1)) if re.search(invoice_number_pattern, text) else "Not found"
    invoice_date = clean_text(re.search(invoice_date_pattern, text).group(1)) if re.search(invoice_date_pattern, text) else "Not found"
    due_date = clean_text(re.search(due_date_pattern, text).group(1)) if re.search(due_date_pattern, text) else "Not found"
    customer_name = clean_text(re.search(customer_pattern, text).group(1)) if re.search(customer_pattern, text) else "Not found"
    total_amount = clean_text(re.search(total_amount_pattern, text).group(1)) if re.search(total_amount_pattern, text) else "Not found"

    place_of_supply_match = re.search(place_of_supply_pattern, text)
    place_of_supply = clean_text(place_of_supply_match.group(1)) if place_of_supply_match else "Not found"

    bank_name_match = re.search(bank_name_pattern, text)
    account_number_match = re.search(account_number_pattern, text)

    bank_name = clean_text(bank_name_match.group(1)) if bank_name_match else "Not found"
    account_number = clean_text(account_number_match.group(1)) if account_number_match else "Not found"

    return {
        "Company Name": company_name,
        "GSTIN": gstin,
        "Phone Number": phone,
        "Email Address": email,
        "Invoice Number": invoice_number,
        "Invoice Date": invoice_date,
        "Due Date": due_date,
        "Customer Name": customer_name,
        "Place of Supply": place_of_supply,
        "Total Amount": total_amount,
        "Bank Name": bank_name,
        "Account Number": account_number
    }


def count_not_found_fields(invoice_data):
    not_found_count = 0
    for value in invoice_data.values():
        if value == "Not found":
            not_found_count += 1
    return not_found_count


def process_files_in_directory(directory_path):
    total_files = 0
    overall_accuracy = 0
    not_found_field_counts = []

    total_fields_per_file = 12

    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)

        if os.path.isfile(file_path):
            total_files += 1
            if file_path.lower().endswith(".pdf"):
                lines = extract_text_from_pdf(file_path)
            else:
                lines = extract_text_from_image(file_path)

            invoice_data = extract_invoice_data(lines)
            not_found_count = count_not_found_fields(invoice_data)
            not_found_field_counts.append(not_found_count)

            # caalculate accuracy for the current file
            accuracy_per_file = ((total_fields_per_file - not_found_count) / total_fields_per_file) * 100
            overall_accuracy += accuracy_per_file

            print(f"Processed file: {file_name}")
            print(f"Not found fields: {not_found_count} out of {total_fields_per_file}")
            print(f"Accuracy for this file: {accuracy_per_file:.2f}%\n")

    # compute overall accuracy
    overall_accuracy = overall_accuracy / total_files if total_files > 0 else 0

    # print summary of results
    print(f"\nSummary:")
    print(f"Total files processed: {total_files}")
    print(f"Overall accuracy: {overall_accuracy:.2f}%")
    print(f"Average 'Not found' fields per file: {sum(not_found_field_counts) / total_files:.2f}" if total_files > 0 else "N/A")


# Specify the directory containing the files to process
directory_path = r"C:\Users\lenovo\Downloads\Jan to Mar-20241016T063925Z-001\Jan to Mar"

# Run the processing function
process_files_in_directory(directory_path)
