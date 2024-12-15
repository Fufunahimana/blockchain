import hashlib
import json
import uuid
import os
import qrcode
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkcalendar import DateEntry
from PIL import ImageTk, Image

# Blockchain Class
class CertificateBlockchain:
    def __init__(self):
        self.chain = []
        self.create_block(previous_hash="0", data="Genesis Block")

    def create_block(self, previous_hash, data):
        """Create a new block with the certificate data."""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.now()),
            'certificate_id': str(uuid.uuid4()),
            'data': data,
            'previous_hash': previous_hash,
            'hash': None
        }
        block['hash'] = self.calculate_hash(block)
        self.chain.append(block)
        return block

    def calculate_hash(self, block):
        """Calculate the SHA-256 hash for the block."""
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_duplicate_certificate(self, certificate_data):
        """Check if a certificate already exists in the blockchain."""
        for block in self.chain:
            if block['data'] == certificate_data:
                return True
        return False

    def display_chain(self):
        """Print all blocks in the blockchain."""
        for block in self.chain:
            print(json.dumps(block, indent=4))


# Certificate Application Class
class CertificateApp:
    def __init__(self, root, blockchain):
        self.root = root
        self.root.title("Certificate Validation System")
        self.blockchain = blockchain

        self.certificates = []  # Store the uploaded certificate information
        self.upload_folder = "uploaded_certificates"  # Folder to save certificates
        os.makedirs(self.upload_folder, exist_ok=True)

        # Form and Table
        self.create_form()
        self.create_table()

    def create_form(self):
        """Create the form for entering certificate details."""
        # Full name input
        tk.Label(self.root, text="Full Name:").grid(row=0, column=0, padx=10, pady=5)
        self.full_name = tk.Entry(self.root)
        self.full_name.grid(row=0, column=1, padx=10, pady=5)

        # Diploma input
        tk.Label(self.root, text="Diploma:").grid(row=1, column=0, padx=10, pady=5)
        self.diploma = tk.Entry(self.root)
        self.diploma.grid(row=1, column=1, padx=10, pady=5)

        # Diploma type input
        tk.Label(self.root, text="Diploma Type:").grid(row=2, column=0, padx=10, pady=5)
        self.diploma_type = tk.Entry(self.root)
        self.diploma_type.grid(row=2, column=1, padx=10, pady=5)

        # Birth Date and Age
        tk.Label(self.root, text="Birth Date:").grid(row=3, column=0, padx=10, pady=5)
        self.birth_date = DateEntry(self.root, date_pattern="yyyy-mm-dd")
        self.birth_date.grid(row=3, column=1, padx=10, pady=5)
        self.birth_date.bind("<<DateEntrySelected>>", self.calculate_age)

        tk.Label(self.root, text="Age:").grid(row=4, column=0, padx=10, pady=5)
        self.age = tk.Entry(self.root, state="readonly")
        self.age.grid(row=4, column=1, padx=10, pady=5)

        # School info
        tk.Label(self.root, text="School Name:").grid(row=5, column=0, padx=10, pady=5)
        self.school_name = tk.Entry(self.root)
        self.school_name.grid(row=5, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Start Date:").grid(row=6, column=0, padx=10, pady=5)
        self.start_date = DateEntry(self.root, date_pattern="yyyy-mm-dd")
        self.start_date.grid(row=6, column=1, padx=10, pady=5)

        tk.Label(self.root, text="End Date:").grid(row=7, column=0, padx=10, pady=5)
        self.end_date = DateEntry(self.root, date_pattern="yyyy-mm-dd")
        self.end_date.grid(row=7, column=1, padx=10, pady=5)

        # Upload button
        self.upload_btn = tk.Button(self.root, text="Upload Certificate", command=self.upload_certificate)
        self.upload_btn.grid(row=8, column=0, columnspan=2, pady=10)

    def calculate_age(self, event):
        """Calculate age from the birthdate."""
        birth_date = self.birth_date.get_date()
        today = datetime.today().date()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        self.age.config(state="normal")
        self.age.delete(0, tk.END)
        self.age.insert(0, str(age))
        self.age.config(state="readonly")

    def create_table(self):
        """Create the table to display certificates."""
        self.treeview = ttk.Treeview(self.root, columns=("Name", "Diploma", "Upload Date"), show="headings")
        self.treeview.grid(row=9, column=0, columnspan=2, sticky="nsew")
        self.treeview.heading("Name", text="Full Name")
        self.treeview.heading("Diploma", text="Diploma")
        self.treeview.heading("Upload Date", text="Upload Date")

    def upload_certificate(self):
        """Upload certificate and validate with blockchain."""
        # Input validation
        full_name = self.full_name.get()
        diploma = self.diploma.get()
        diploma_type = self.diploma_type.get()
        birth_date = self.birth_date.get_date()
        school_name = self.school_name.get()
        start_date = self.start_date.get_date()
        end_date = self.end_date.get_date()

        if not all([full_name, diploma, diploma_type, school_name]):
            messagebox.showerror("Error", "Fill all the required fields!")
            return

        # File upload
        cert_file = filedialog.askopenfilename(title="Select Certificate", filetypes=[("PDF Files", "*.pdf"),
                                                                                      ("Image Files", "*.jpg;*.jpeg;*.png")])
        if not cert_file:
            messagebox.showerror("Error", "No certificate file selected!")
            return

        # Save file to folder
        cert_filename = os.path.basename(cert_file)
        dest_path = os.path.join(self.upload_folder, cert_filename)
        shutil.copy(cert_file, dest_path)

        # Prepare certificate data
        certificate_data = {
            "full_name": full_name,
            "diploma": diploma,
            "diploma_type": diploma_type,
            "birth_date": str(birth_date),
            "school_name": school_name,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "certificate_file": dest_path
        }

        # Blockchain validation
        if self.blockchain.is_duplicate_certificate(certificate_data):
            messagebox.showerror("Error", "Certificate already uploaded!")
            return

        self.blockchain.create_block(previous_hash=self.blockchain.chain[-1]['hash'], data=certificate_data)

        # QR Code generation
        qr = qrcode.make(dest_path)
        qr_path = os.path.join(self.upload_folder, f"{full_name}_qr.png")
        qr.save(qr_path)

        # Update table
        upload_date = str(datetime.now())
        self.treeview.insert("", "end", values=(full_name, diploma, upload_date))
        messagebox.showinfo("Success", "Certificate uploaded successfully!")

# Main Execution
if __name__ == "__main__":
    root = tk.Tk()
    blockchain = CertificateBlockchain()
    app = CertificateApp(root, blockchain)
    root.mainloop()
