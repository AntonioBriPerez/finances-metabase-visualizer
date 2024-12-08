import email
from email.header import decode_header
import imaplib
import os
import time
import json
import logging
import hashlib
from dotenv import load_dotenv
from doclingparser import parse_nomina

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PayrollTracker:
    def __init__(self, tracking_file='processed_payrolls.json'):
        self.tracking_file = tracking_file
        self.processed_files = self._load_processed_files()

    def _load_processed_files(self):
        try:
            if os.path.exists(self.tracking_file):
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Error loading tracking file: {e}")
            return {}

    def update_processed_files(self, email_id, filename, file_hash):
        try:
            self.processed_files[email_id] = {
                'filename': filename,
                'hash': file_hash
            }
            with open(self.tracking_file, 'w') as f:
                json.dump(self.processed_files, f)
            logging.info(f"Updated processed files with email ID: {email_id}, filename: {filename}, hash: {file_hash}")
        except Exception as e:
            logging.error(f"Error updating tracking file: {e}")

    def has_been_processed(self, file_hash):
        return any(file_info['hash'] == file_hash for file_info in self.processed_files.values())

def compute_file_hash(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def download_payroll_attachments(email_message, download_path=None, tracker=None, reprocess_all=False):
    if download_path is None:
        download_path = os.getcwd()
    
    os.makedirs(download_path, exist_ok=True)
    
    downloaded_attachments = []
    
    for part in email_message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        
        filename = part.get_filename()
        if filename and filename.lower().endswith(('.pdf', '.xlsx', '.xls')):
            try:
                filename = decode_header(filename)[0][0]
                if isinstance(filename, bytes):
                    filename = filename.decode()
                
                filepath = os.path.join(download_path, filename)
                
                base, extension = os.path.splitext(filename)
                counter = 1
                while os.path.exists(filepath):
                    filename = f"{base}_{counter}{extension}"
                    filepath = os.path.join(download_path, filename)
                    counter += 1
                
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                
                file_hash = compute_file_hash(filepath)
                if tracker and tracker.has_been_processed(file_hash) and not reprocess_all:
                    logging.info(f"Skipping already processed file: {filename}")
                    os.remove(filepath)
                    continue
                
                downloaded_attachments.append(filepath)
                logging.info(f"Downloaded payroll attachment: {filename}")
            
            except Exception as e:
                logging.error(f"Error downloading attachment: {e}")
    
    return downloaded_attachments

def get_icloud_emails(username, password, num_emails=5, download_path=None, tracker=None, reprocess_all=False):
    IMAP_SERVER = os.getenv('IMAP_HOST_ICLOUD')

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(username, password)
        mail.select('Nominas')
        logging.info("Connected to IMAP server and selected 'Nominas' folder")
        
        _, search_data = mail.search(None, 'ALL')
        email_ids = search_data[0].split()
        
        email_ids = email_ids[::-1]
        
        for email_id in email_ids:
            email_id_str = email_id.decode()
            
            _, email_data = mail.fetch(email_id, '(BODY[])')
            raw_email = email_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            attachments = download_payroll_attachments(
                email_message, 
                download_path, 
                tracker, 
                reprocess_all
            )
            
            if attachments and tracker:
                for attachment in attachments:
                    file_hash = compute_file_hash(attachment)
                    tracker.update_processed_files(email_id_str, attachment, file_hash)
                break
        
        mail.close()
        mail.logout()
        logging.info("Disconnected from IMAP server")
        return attachments
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def main():
    load_dotenv()
    USERNAME = os.getenv('IMAP_USER_ICLOUD')
    PASSWORD = os.getenv('IMAP_PASS_ICLOUD')
    DOWNLOAD_PATH = os.path.join(os.getcwd(), 'payroll_attachments')
    
    tracker = PayrollTracker()
    
    import sys
    reprocess_all = '--reprocess' in sys.argv
    
    while True:
        logging.info("Checking for new payroll emails")
        nominas_path = get_icloud_emails(
            USERNAME, 
            PASSWORD, 
            download_path=DOWNLOAD_PATH,
            tracker=tracker,
            reprocess_all=reprocess_all
        )
        for p in nominas_path:
            df = parse_nomina(p)
            logging.info(f"Parsed payroll file: {p}")
        time.sleep(30)

if __name__ == "__main__":
    main()
