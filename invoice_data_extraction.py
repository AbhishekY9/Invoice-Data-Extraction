import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import pdfplumber
import pytesseract
import os
import re

root = tk.Tk()
root.title("Zolvit - Invoice Extractor")
root.geometry("1200x800")
root.configure(bg="white")

logo_label = tk.Label(root, bg="white")
logo_label.pack(pady=20)

company_name_label = tk.Label(root, text="Zolvit", bg="white", font=("Arial", 24, "bold"), fg="black")
company_name_label.pack(pady=10)

results_frame = tk.Frame(root, bg="white")
results_frame.pack(pady=20)

def load_logo(image_path):
    try:
        logo_image = Image.open(image_path)
        original_width, original_height = logo_image.size
        new_width = original_width // 2
        new_height = original_height // 2
        logo_image = logo_image.resize((new_width, new_height))
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label.config(image=logo_photo)
        logo_label.image = logo_photo
    except Exception as e:
        print(f"Error loading image: {e}")

def upload_file():
    file_path = filedialog.askopenfilename(
        title="Select an Image or PDF",
        filetypes=[("Image/PDF Files", "*.png;*.jpg;*.jpeg;*.pdf")]
    )
    if file_path:
        print(f"Selected file: {file_path}")
        main(file_path)

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

def extract_item_amounts(lines):
    item_amounts = []
    for line in lines:
        match = re.search(r"%\) ([\d,]+\.\d{2})", line)
        if match:
            amount = float(match.group(1).replace(",", ""))
            item_amounts.append(amount)
    return item_amounts

def sum_item_amounts(item_amounts):
    return round(sum(item_amounts), 0)

def display_results(invoice_data, item_amounts, total_item_sum):
    for widget in results_frame.winfo_children():
        widget.destroy()

    results_text = "Extracted Invoice Data:\n"
    for key, value in invoice_data.items():
        results_text += f"{key}: {value}\n"

    results_text += "\nExtracted Item Amounts:\n"
    for idx, amount in enumerate(item_amounts, 1):
        results_text += f"Item {idx} Amount: {amount:.2f}\n"

    results_text += f"\nSum of Item Amounts: {total_item_sum:.2f}\n"

    try:
        total_amount = float(invoice_data['Total Amount'].replace(",", ""))
        if total_item_sum == total_amount:
            results_text += "\nSum of calculated item amounts is equal to Total Amount. Extracted Data is Trusted."
        else:
            results_text += "\nSum of calculated item amounts is NOT equal to Total Amount. Extracted Data is NOT Trusted."
    except ValueError:
        results_text += "\nTotal Amount could not be parsed. Please check the extracted data."

    results_label = tk.Label(results_frame, text=results_text, bg="white", font=("Arial", 12), anchor="w", justify="left")
    results_label.pack(padx=10, pady=10)

def main(file_path):
    if file_path.lower().endswith(".pdf"):
        lines = extract_text_from_pdf(file_path)
    else:
        lines = extract_text_from_image(file_path)

    invoice_data = extract_invoice_data(lines)
    item_amounts = extract_item_amounts(lines)
    total_item_sum = sum_item_amounts(item_amounts)
    display_results(invoice_data, item_amounts, total_item_sum)

upload_button = tk.Button(root, text="Upload Invoice", command=upload_file, bg="#4CAF50", fg="white", font=("Arial", 16))
upload_button.pack(pady=20)

load_logo(r"C:\Users\lenovo\Downloads\images (2).png")

root.mainloop()
