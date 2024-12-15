import hashlib
import json
import uuid
from datetime import datetime
import os
import qrcode
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkcalendar import DateEntry
from PIL import Image, ImageTk

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

# Certificate Application Class
class CertificateApp:
    def __init__(self, root, blockchain):
        self.root = root
        self.root.title("Certificate Validation System")
        self.root.geometry("1200x780")
        self.root.configure(bg="cyan")
        self.blockchain = blockchain

        self.certificates = []  # To store the uploaded certificate information
        self.upload_folder = "uploaded_certificates"  # Folder where certificates will be saved
        os.makedirs(self.upload_folder, exist_ok=True)  # Create folder if it doesn't exist

        # Image Placeholder
        self.current_image = None
        self.image_visible = True

        # Create the form
        self.create_form()

    def create_form(self):
        """Create the form for entering certificate details."""
        # Full name input
        tk.Label(self.root, text="Nom Complet:",font=("Times New Roman", 15),bg="cyan").grid(row=0, column=0,)
        self.full_name = tk.Entry(self.root,width=20,bg="white",font=("Times New Roman", 15))
        self.full_name.grid(row=0, column=1, pady=10, padx=10)

        # Diploma input
        tk.Label(self.root, text="Diplome Obtenu:",font=("Times New Roman", 15),bg="cyan").grid(row=1, column=0)
        self.diploma = tk.Entry(self.root,width=20,bg="white",font=("Times New Roman", 15))
        self.diploma.grid(row=1, column=1, pady=10, padx=10)

        # Diploma type input
        tk.Label(self.root, text="Domaine:",font=("Times New Roman", 15),bg="cyan").grid(row=2, column=0)
        self.diploma_type = tk.Entry(self.root,width=20,bg="white",font=("Times New Roman", 15))
        self.diploma_type.grid(row=2, column=1, pady=10, padx=10)

        # Birth date input with Age autofill
        tk.Label(self.root, text="Date de Naissance:",font=("Times New Roman", 15),bg="cyan").grid(row=3, column=0)
        self.birth_date = DateEntry(self.root,width=18,bg="white",font=("Times New Roman", 15), date_pattern="yyyy-mm-dd")
        self.birth_date.grid(row=3, column=1, pady=10, padx=10)
        self.birth_date.bind("<<DateEntrySelected>>", self.calculate_age)

        # Age field
        tk.Label(self.root, text="Age:",font=("Times New Roman", 15),bg="cyan").grid(row=4, column=0)
        self.age = tk.Entry(self.root,width=20,bg="gray",font=("Times New Roman", 15), state="readonly")
        self.age.grid(row=4, column=1, pady=10, padx=10)

        # School information
        tk.Label(self.root, text="Nom de l'ecole:",font=("Times New Roman", 15),bg="cyan").grid(row=5, column=0)
        self.school_name = tk.Entry(self.root,width=20,bg="white",font=("Times New Roman", 15))
        self.school_name.grid(row=5, column=1, pady=10, padx=10)

        tk.Label(self.root, text="Date Début:",font=("Times New Roman", 15),bg="cyan").grid(row=6, column=0)
        self.start_date = DateEntry(self.root,width=18,bg="white",font=("Times New Roman", 15), date_pattern="yyyy-mm-dd")
        self.start_date.grid(row=6, column=1, pady=10, padx=10)

        tk.Label(self.root, text="Date Fin:",font=("Times New Roman", 15),bg="cyan").grid(row=7, column=0)
        self.end_date = DateEntry(self.root,width=18,bg="white",font=("Times New Roman", 15), date_pattern="yyyy-mm-dd")
        self.end_date.grid(row=7, column=1, pady=10, padx=10)

        # Certificate Image Display
        self.image_label = tk.Label(self.root, text="No Image", bg="grey", width=40, height=10)
        self.image_label.grid(row=0, column=3, rowspan=4, padx=10)

        # QR Code Display
        self.qr_label = tk.Label(self.root, text="QR Code", bg="white", width=40, height=10)
        self.qr_label.grid(row=4, column=3, rowspan=4, padx=10)

        # Upload certificate button
        self.upload_btn = tk.Button(self.root, text="Upload Certificate", fg ="red",width=15,font=("Times New Roman", 15,"bold"),bg="black",command=self.upload_certificate)
        self.upload_btn.grid(row=8, column=0, columnspan=2,pady=10, padx=10)

        # Toggle Image Button
        self.toggle_image_btn = tk.Button(self.root, text="Show/Hide Certificate Image", fg ="red",width=25,font=("Times New Roman", 15,"bold"),bg="green", command=self.toggle_image)
        self.toggle_image_btn.grid(row=8, column=2)

        # Exit Button
        self.exit_btn = tk.Button(self.root, text="Exit", fg ="black",width=15,font=("Times New Roman", 15,"bold"),bg="red", command=self.root.quit)
        self.exit_btn.grid(row=8, column=3)

        # Certificate Table
        # Certificate Table
        columns = ("Name", "Diploma", "Upload Date")
        self.treeview = ttk.Treeview(self.root, columns=columns, show="headings", height=10)  # Set height for rows
        self.treeview.heading("Name", text="Full Name")
        self.treeview.heading("Diploma", text="Diploma")
        self.treeview.heading("Upload Date", text="Upload Date")
        
        # Adjust column widths
        self.treeview.column("Name", width=300)
        self.treeview.column("Diploma", width=300)
        self.treeview.column("Upload Date", width=300)
        
        self.treeview.grid(row=9, column=0, columnspan=4, padx=10, pady=10)
        self.treeview.bind("<ButtonRelease-1>", self.display_certificate_details)


    def calculate_age(self, event):
        """Calculate age from the selected birthdate."""
        birth_date = self.birth_date.get_date()
        today = datetime.today().date()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        self.age.config(state="normal")
        self.age.delete(0, tk.END)
        self.age.insert(0, str(age))
        self.age.config(state="readonly")

    def upload_certificate(self):
        """Upload the certificate and add it to the blockchain."""
        # Validate inputs
        full_name = self.full_name.get()
        diploma = self.diploma.get()
        if not full_name or not diploma:
            messagebox.showerror("Error", "Fill all required fields!")
            return

        cert_file = filedialog.askopenfilename(title="Select Certificate File", filetypes=[("Image Files", "*.jpg;*.png")])
        if not cert_file:
            messagebox.showerror("Error", "No certificate file selected!")
            return

        # Copy certificate to upload folder
        cert_filename = os.path.basename(cert_file)
        dest_path = os.path.join(self.upload_folder, cert_filename)
        shutil.copy(cert_file, dest_path)

        # Generate and save QR code
        qr = qrcode.make(dest_path)
        qr_path = os.path.join(self.upload_folder, f"{full_name}_qr.png")
        qr.save(qr_path)

        # Add certificate to blockchain
        certificate_data = {
            "full_name": full_name,
            "diploma": diploma,
            "file_path": dest_path,
            "qr_path": qr_path
        }
        self.blockchain.create_block(self.blockchain.chain[-1]['hash'], certificate_data)

        # Add to table
        self.treeview.insert("", "end", values=(full_name, diploma, str(datetime.now().date())))
        messagebox.showinfo("Success", "Certificate uploaded successfully!")

    def display_certificate_details(self, event):
        """Display image and QR code for selected certificate."""
        selected_item = self.treeview.selection()[0]
        full_name = self.treeview.item(selected_item, 'values')[0]
        
        # Safely iterate and check for valid data
        cert = next(
            (b['data'] for b in self.blockchain.chain 
             if isinstance(b['data'], dict) and b['data'].get('full_name') == full_name),
            None
        )
        
        if cert:
            # Display certificate image
            img = Image.open(cert['file_path']).resize((400, 300))
            self.current_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.current_image, text="")
            
            # Display QR code
            qr_img = Image.open(cert['qr_path']).resize((400, 300))
            self.current_qr = ImageTk.PhotoImage(qr_img)
            self.qr_label.config(image=self.current_qr, text="")
        else:
            messagebox.showerror("Error", "Certificate details not found.")

    def toggle_image(self):
        """Toggle visibility of the certificate image."""
        if self.image_visible:
            self.image_label.config(image="", text="No Image")
        else:
            selected_item = self.treeview.selection()
            if selected_item:
                self.display_certificate_details(None)
        self.image_visible = not self.image_visible

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    blockchain = CertificateBlockchain()
    app = CertificateApp(root, blockchain)
    root.mainloop()
