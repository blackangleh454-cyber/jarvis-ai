#!/usr/bin/env python3
"""email-manager - Read, write, send emails via IMAP/SMTP."""
import sys
import os
import json
import base64
from datetime import datetime

CONFIG_FILE = os.path.expanduser("~/.jarvis_email_config.json")


def load_config():
    if os.path.exists(CONFIG_FILE):
        return json.load(open(CONFIG_FILE))
    return None


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def configure(email, smtp, imap, user, password):
    """Configure email account."""
    config = {
        "email": email,
        "smtp_server": smtp,
        "imap_server": imap,
        "username": user,
        "password": password
    }
    save_config(config)
    return f"Email configured: {email}"


def connect_imap():
    """Connect to IMAP server."""
    config = load_config()
    if not config:
        return None, "Email not configured"

    try:
        import imaplib
        mail = imaplib.IMAP4_SSL(config["imap_server"])
        mail.login(config["username"], config["password"])
        return mail, None
    except Exception as e:
        return None, f"IMAP error: {e}"


def connect_smtp():
    """Connect to SMTP server."""
    config = load_config()
    if not config:
        return None, "Email not configured"

    try:
        import smtplib
        import ssl
        context = ssl.create_default_context()
        mail = smtplib.SMTP_SSL(config["smtp_server"], 465, context=context)
        mail.login(config["username"], config["password"])
        return mail, None
    except Exception as e:
        return None, f"SMTP error: {e}"


def list_emails(folder="INBOX", limit=10):
    """List emails in folder."""
    mail, err = connect_imap()
    if err:
        return err

    try:
        mail.select(folder)
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()[-limit:]

        lines = [f"Emails in {folder}:"]
        for eid in reversed(email_ids):
            status, msg = mail.fetch(eid, "(ENVELOPE)")
            if status == "OK":
                envelope = msg[0][1]
                subject = envelope.subject.decode() if hasattr(envelope, 'subject') else "No subject"
                from_addr = envelope.from_[0].mailbox.decode() + "@" + envelope.from_[0].host.decode() if envelope.from_ else "unknown"
                lines.append(f"  [{eid.decode()}] {from_addr}: {subject[:50]}")

        mail.close()
        mail.logout()
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def list_unread():
    """List unread emails."""
    mail, err = connect_imap()
    if err:
        return err

    try:
        mail.select("INBOX")
        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()

        if not email_ids:
            return "No unread emails"

        lines = [f"Unread emails ({len(email_ids)}):"]
        for eid in email_ids[:20]:
            status, msg = mail.fetch(eid, "(ENVELOPE)")
            if status == "OK":
                envelope = msg[0][1]
                subject = getattr(envelope, 'subject', b'No subject').decode() if hasattr(envelope, 'subject') else "No subject"
                lines.append(f"  [{eid.decode()}] {subject[:60]}")

        mail.close()
        mail.logout()
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def read_email(email_id):
    """Read specific email."""
    mail, err = connect_imap()
    if err:
        return err

    try:
        mail.select("INBOX")
        status, msg = mail.fetch(email_id, "(BODY.PEEK[])")
        if status != "OK":
            return f"Email not found: {email_id}"

        from email import message_from_bytes
        message = message_from_bytes(msg[0][1])

        lines = [f"Email #{email_id}:"]
        lines.append(f"From: {message.get('From')}")
        lines.append(f"To: {message.get('To')}")
        lines.append(f"Subject: {message.get('Subject')}")
        lines.append(f"Date: {message.get('Date')}")
        lines.append("")

        body = ""
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = message.get_payload(decode=True).decode()

        lines.append(body[:3000])
        mail.close()
        mail.logout()
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def send_email(to_addr, subject, body):
    """Send an email."""
    mail, err = connect_smtp()
    if err:
        return err

    config = load_config()
    try:
        msg = f"From: {config['email']}\nTo: {to_addr}\nSubject: {subject}\n\n{body}"
        mail.sendmail(config["email"], to_addr, msg)
        mail.quit()
        return f"Email sent to {to_addr}: {subject}"
    except Exception as e:
        return f"Send error: {e}"


def reply_email(email_id, reply_body):
    """Reply to an email."""
    mail, err = connect_imap()
    if err:
        return err

    try:
        mail.select("INBOX")
        status, msg = mail.fetch(email_id, "(ENVELOPE)")
        if status != "OK":
            return "Email not found"

        from email import message_from_bytes
        message = message_from_bytes(msg[0][1])
        to_addr = message.get("Reply-To") or message.get("From")

        config = load_config()
        subject = message.get("Subject", "")
        if not subject.startswith("Re:"):
            subject = "Re: " + subject

        smtp, smtp_err = connect_smtp()
        if smtp_err:
            return smtp_err

        msg = f"From: {config['email']}\nTo: {to_addr}\nSubject: {subject}\nIn-Reply-To: {message.get('Message-ID')}\n\n{reply_body}"
        smtp.sendmail(config["email"], to_addr, msg)
        smtp.quit()

        mail.close()
        mail.logout()
        return f"Reply sent to {to_addr}"
    except Exception as e:
        return f"Error: {e}"


def list_attachments(email_id):
    """List email attachments."""
    mail, err = connect_imap()
    if err:
        return err

    try:
        mail.select("INBOX")
        status, msg = mail.fetch(email_id, "(BODY.PEEK[])")
        if status != "OK":
            return "Email not found"

        from email import message_from_bytes
        message = message_from_bytes(msg[0][1])

        lines = ["Attachments:"]
        found = False
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                found = True
                filename = part.get_filename()
                size = len(part.get_payload(decode=True)) if part.get_payload() else 0
                lines.append(f"  {filename} ({size} bytes)")

        mail.close()
        mail.logout()
        return "\n".join(lines) if found else "No attachments"
    except Exception as e:
        return f"Error: {e}"


def search_emails(query):
    """Search emails."""
    mail, err = connect_imap()
    if err:
        return err

    try:
        mail.select("INBOX")
        status, messages = mail.search(None, f'SUBJECT "{query}"')
        email_ids = messages[0].split()

        if not email_ids:
            return f"No emails matching '{query}'"

        lines = [f"Found {len(email_ids)} emails:"]
        for eid in email_ids[:20]:
            lines.append(f"  {eid.decode()}")

        mail.close()
        mail.logout()
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def delete_email(email_id):
    """Delete an email."""
    mail, err = connect_imap()
    if err:
        return err

    try:
        mail.select("INBOX")
        mail.store(email_id, "+FLAGS", "\\Deleted")
        mail.expunge()
        mail.close()
        mail.logout()
        return f"Email {email_id} deleted"
    except Exception as e:
        return f"Error: {e}"


def send_with_attachment(to_addr, subject, body, file_path):
    """Send email with attachment."""
    mail, err = connect_smtp()
    if err:
        return err

    config = load_config()
    try:
        from email import encoders
        from email.mime.base import MIMEBase
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg["From"] = config["email"]
        msg["To"] = to_addr
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with open(file_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(part)

        mail.sendmail(config["email"], to_addr, msg.as_string())
        mail.quit()
        return f"Email with attachment sent to {to_addr}"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "config":
        print(configure(a[0], a[1], a[2], a[3], a[4]) if len(a) >= 5 else "Usage: config <email> <smtp> <imap> <user> <pass>")
    elif cmd == "list":
        print(list_emails(a[0] if a else "INBOX", int(a[1]) if len(a) > 1 and a[1].isdigit() else 10))
    elif cmd == "unread":
        print(list_unread())
    elif cmd == "read":
        print(read_email(a[0]) if a else "Usage: read <email_id>")
    elif cmd == "send":
        print(send_email(a[0], a[1], " ".join(a[2:])) if len(a) >= 3 else "Usage: send <to> <subject> <body>")
    elif cmd == "reply":
        print(reply_email(a[0], " ".join(a[1:])) if len(a) >= 2 else "Usage: reply <email_id> <body>")
    elif cmd == "attachments":
        print(list_attachments(a[0]) if a else "Usage: attachments <email_id>")
    elif cmd == "search":
        print(search_emails(" ".join(a)) if a else "Usage: search <query>")
    elif cmd == "delete":
        print(delete_email(a[0]) if a else "Usage: delete <email_id>")
    elif cmd == "send_attachment":
        print(send_with_attachment(a[0], a[1], a[2], a[3]) if len(a) >= 4 else "Usage: send_attachment <to> <subject> <body> <file>")
    else:
        print("Commands: config, list, unread, read, send, reply, attachments, search, delete, send_attachment")
