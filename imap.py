import email
from email.header import decode_header
import imaplib
import os
import time
import logging
import shutil
from src.aux_functions import generar_hash_archivo
from src.Database import Database
from dotenv import load_dotenv
from doclingparser import parse_nomina

# Configuración del logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def download_payroll_attachments(
    email_message, download_path=None, db=None, reprocess_all=False
):
    if download_path is None:
        download_path = os.getcwd()

    os.makedirs(download_path, exist_ok=True)

    downloaded_attachments = []

    for part in email_message.walk():
        if part.get_content_maintype() == "multipart":
            continue

        filename = part.get_filename()
        if filename and filename.lower().endswith((".pdf", ".xlsx", ".xls")):
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

                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))

                file_hash = generar_hash_archivo(filepath)
                if db and not reprocess_all:
                    existing_hashes = db.get_existing_hashes("nominas")
                    if file_hash in existing_hashes:
                        logging.info(f"Skipping already processed file: {filename}")
                        os.remove(filepath)
                        continue

                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                downloaded_attachments.append(filepath)
                logging.info(f"Downloaded payroll attachment: {filename}")

            except Exception as e:
                logging.error(f"Error downloading attachment: {e}")

    return downloaded_attachments


def get_icloud_emails(
    username, password, num_emails=5, download_path=None, db=None, reprocess_all=False
):
    IMAP_SERVER = os.getenv("IMAP_HOST_ICLOUD")

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(username, password)
        mail.select("Nominas")
        logging.info("Connected to IMAP server and selected 'Nominas' folder")

        _, search_data = mail.search(None, "ALL")
        email_ids = search_data[0].split()

        email_ids = email_ids[::-1]

        for email_id in email_ids:
            email_id_str = email_id.decode()

            _, email_data = mail.fetch(email_id, "(BODY[])")
            raw_email = email_data[0][1]
            email_message = email.message_from_bytes(raw_email)

            attachments = download_payroll_attachments(
                email_message, download_path, db, reprocess_all
            )

            if attachments:
                break

        mail.close()
        mail.logout()
        logging.info("Disconnected from IMAP server")
        return attachments

    except Exception as e:
        logging.error(f"An error occurred: {e}")


def main():
    load_dotenv()
    USERNAME = os.getenv("IMAP_USER_ICLOUD")
    PASSWORD = os.getenv("IMAP_PASS_ICLOUD")
    DOWNLOAD_PATH = os.path.join(os.getcwd(), "payroll_attachments")

    import sys

    reprocess_all = "--reprocess" in sys.argv
    db = Database(
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"),
        database=os.getenv("PG_DBNAME"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASS"),
    )
    while True:

        logging.info("Checking for new payroll emails")
        nominas_path = get_icloud_emails(
            USERNAME,
            PASSWORD,
            download_path=DOWNLOAD_PATH,
            db=db,
            reprocess_all=reprocess_all,
        )
        for p in nominas_path:
            df = parse_nomina(p)
            db.insert_dataframe(df, "nominas", if_exists="append", index=False)
            logging.info(f"Parsed payroll file: {p}")
        time.sleep(int(os.getenv("SLEEP_TIME")))


if __name__ == "__main__":
    main()
