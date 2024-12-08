import email
import imaplib
import os
from dotenv import load_dotenv
load_dotenv()

imap_host_icloud = os.getenv('IMAP_HOST_ICLOUD')
imap_user_icloud = os.getenv('IMAP_USER_ICLOUD')
imap_pass_icloud = os.getenv('IMAP_PASS_ICLOUD')


m = imaplib.IMAP4_SSL(imap_host_icloud)
m.login(imap_user_icloud, imap_pass_icloud)
m.select('Inbox')
