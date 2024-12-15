import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
import hashlib
import os
import qrcode
from datetime import datetime
from PIL import Image, ImageTk

# Constants
CERTIFICATE_DIR = "uploaded_certificates"

# Ensure the directory exists
if not os.path.exists(CERTIFICATE_DIR):
    os.mkdir(CERTIFICATE_DIR)

# Data structure to store certificates
certificates = []

# Helper functions
def calculate_hash(filepath):
    """Generate SHA-256 hash for the file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def validate_file_format(filepath):
    """Check if file format is valid."""
    valid_formats = (".png", ".jpg", ".jpeg", ".pdf", ".tif")
    return filepath.lower().endswith(valid_formats)

def clear_form():
    """Clear all fields in the form."""
    name_entry.delete(0, tk.END)
    diploma_entry.delete(0, tk.END)
    diploma_type_entry.delete(0, tk.END)
    birth_date_entry.set_date(datetime.now())
    school_entry.delete(0, tk.END)
    begin_date_entry.set_date(datetime.now())
    end_date_entry.set_date(datetime.now())
    certificate_image_label.config(image="")
    qr_label.config(image="")
    hash_label.config(text="")
    age_label.config(text="Age: ")

def load_existing_certificates():
    """Load existing certificates from the folder."""
    for filename in os.listdir(CERTIFICATE_DIR):
        filepath = os.path.join(CERTIFICATE_DIR, filename)
        if not validate_file_format(filepath):
            continue
        
        file_hash = calculate_hash(filepath)
        upload_date = datetime.fromtimestamp(os.path.getctime(filepath)).strftime("%Y-%m-%d %H:%M:%S")
        certificates.append({
            "name": "Unknown",  # Placeholder for name
            "type": "Unknown",  # Placeholder for type
            "upload_date": upload_date,
            "hash_code": file_hash,
            "file_path": filepath,
            "qr_path": ""  # QR path will be generated dynamically
        })
        certificate_table.insert("", tk.END, values=("Unknown", "Unknown", upload_date, file_hash))

def upload_certificate():
    """Handle certificate upload."""
    filepath = filedialog.askopenfilename(title="Select Certificate")
    if not filepath:
        return

    # Validate file format
    if not validate_file_format(filepath):
        messagebox.showerror("Error", "Invalid file format. Only images or PDFs are allowed.")
        return

    # Get form data
    name = name_entry.get().strip()
    diploma = diploma_entry.get().strip()
    diploma_type = diploma_type_entry.get().strip()
    birth_date = birth_date_entry.get_date()
    school = school_entry.get().strip()
    begin_date = begin_date_entry.get_date()
    end_date = end_date_entry.get_date()

    # Validate form data
    if not all([name, diploma, diploma_type, school]):
        messagebox.showerror("Error", "Please fill all required fields.")
        return

    # Check for duplicates
    for cert in certificates:
        if cert["name"] == name and cert["type"] == diploma_type:
            messagebox.showerror("Error", "Values already exist.")
            return

    # Save file and generate hash
    filename = os.path.basename(filepath)
    dest_path = os.path.join(CERTIFICATE_DIR, filename)
    os.replace(filepath, dest_path)
    file_hash = calculate_hash(dest_path)

    # Generate QR code
    qr_img = qrcode.make(file_hash)
    qr_path = os.path.join(CERTIFICATE_DIR, f"{filename}_qr.png")
    qr_img.save(qr_path)

    # Add certificate data
    certificates.append({
        "name": name,
        "type": diploma_type,
        "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hash_code": file_hash,
        "file_path": dest_path,
        "qr_path": qr_path
    })

    # Update table
    certificate_table.insert("", tk.END, values=(name, diploma_type, datetime.now().strftime("%Y-%m-%d"), file_hash))
    messagebox.showinfo("Success", "Thank you for uploading your certificate.")
    clear_form()

def show_certificate_details(event):
    """Display details of selected certificate."""
    selected_item = certificate_table.selection()
    if not selected_item:
        return

    cert_index = certificate_table.index(selected_item[0])
    cert = certificates[cert_index]

    # Display QR code
    if os.path.exists(cert["qr_path"]):
        qr_img = Image.open(cert["qr_path"])
        qr_img = qr_img.resize((150, 150))
        qr_photo = ImageTk.PhotoImage(qr_img)
        qr_label.config(image=qr_photo)
        qr_label.image = qr_photo

    # Display certificate image (if image file)
    if cert["file_path"].lower().endswith((".png", ".jpg", ".jpeg")):
        cert_img = Image.open(cert["file_path"])
        cert_img = cert_img.resize((300, 300))
        cert_photo = ImageTk.PhotoImage(cert_img)
        certificate_image_label.config(image=cert_photo)
        certificate_image_label.image = cert_photo

    # Display hash code
    hash_label.config(text=f"Hash Code: {cert['hash_code']}")

def calculate_age():
    """Calculate age based on birth date."""
    birth_date = birth_date_entry.get_date()
    today = datetime.now().date()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    age_label.config(text=f"Age: {age}")

def exit_application():
    """Exit the application."""
    app.quit()

# UI Setup
app = tk.Tk()
app.title("Certificate Validation")
app.geometry("1200x800")
app.configure(bg="cyan")

# Add Scrollbar to Main Root
main_canvas = tk.Canvas(app, bg="cyan")
main_scrollbar = ttk.Scrollbar(app, orient=tk.VERTICAL, command=main_canvas.yview)
main_canvas.configure(yscrollcommand=main_scrollbar.set)
main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root_frame = tk.Frame(main_canvas, bg="cyan")
main_canvas.create_window((0, 0), window=root_frame, anchor="nw")
root_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

# Form Frame
form_frame = tk.Frame(root_frame, bg="cyan")
form_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Form Fields
tk.Label(form_frame, text="Nom Complet:", font=("Times New Roman", 15), bg="cyan").grid(row=0, column=0, sticky=tk.W)
name_entry = tk.Entry(form_frame, font=("Times New Roman", 15), bg="white")
name_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(form_frame, text="Niveau d'etude",font=("Times New Roman", 15),bg="cyan").grid(row=1, column=0, sticky=tk.W)
diploma_entry = tk.Entry(form_frame,font=("Times New Roman", 15),bg="white")
diploma_entry.grid(row=1, column=1,padx=10,pady=10)

tk.Label(form_frame, text="Domaine d'étude",font=("Times New Roman", 15),bg="cyan").grid(row=2, column=0, sticky=tk.W)
diploma_type_entry = tk.Entry(form_frame,font=("Times New Roman", 15),bg="white")
diploma_type_entry.grid(row=2, column=1,padx=10,pady=10)

tk.Label(form_frame, text="Date de naissance",font=("Times New Roman", 15),bg="cyan").grid(row=3, column=0, sticky=tk.W)
birth_date_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd",font=("Times New Roman", 18),bg="white")
birth_date_entry.grid(row=3, column=1,padx=10,pady=10)
birth_date_entry.bind("<FocusOut>", lambda e: calculate_age())

age_label = tk.Label(form_frame, text="Age: ",font=("Times New Roman", 15),bg="cyan")
age_label.grid(row=4, column=0, columnspan=2, sticky=tk.W)

tk.Label(form_frame, text="Ecole fréquente",font=("Times New Roman", 15),bg="cyan").grid(row=5, column=0, sticky=tk.W)
school_entry = tk.Entry(form_frame,font=("Times New Roman", 15),bg="white")
school_entry.grid(row=5, column=1,padx=20,pady=10)

tk.Label(form_frame, text="Date du début",font=("Times New Roman", 18),bg="cyan").grid(row=6, column=0, sticky=tk.W)
begin_date_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd",font=("Times New Roman", 15),bg="white")
begin_date_entry.grid(row=6, column=1,padx=20,pady=10)

tk.Label(form_frame, text="Date de fin",font=("Times New Roman", 18),bg="cyan").grid(row=7, column=0, sticky=tk.W)
end_date_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd",font=("Times New Roman", 15),bg="white")
end_date_entry.grid(row=7, column=1,padx=20,pady=10)

# Add remaining form fields as before...

# QR Code and Certificate Display
qr_label = tk.Label(form_frame)
qr_label.grid(row=8, column=0, columnspan=2)

certificate_image_label = tk.Label(form_frame)
certificate_image_label.grid(row=9, column=0, columnspan=2)

hash_label = tk.Label(form_frame, text="")
hash_label.grid(row=10, column=0, columnspan=2)

# Table Frame
table_frame = tk.Frame(root_frame)
table_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

columns = ("Name", "Diploma Type", "Upload Date", "Hash Code")
certificate_table = ttk.Treeview(table_frame, columns=columns, show="headings")
for col in columns:
    certificate_table.heading(col, text=col)

# Add Scrollbar to Table
table_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=certificate_table.yview)
certificate_table.configure(yscrollcommand=table_scrollbar.set)
table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
certificate_table.pack(fill=tk.BOTH, expand=True)

certificate_table.bind("<ButtonRelease-1>", show_certificate_details)

# Load existing certificates
load_existing_certificates()

app.mainloop()
