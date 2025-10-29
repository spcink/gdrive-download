import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from docx2pdf import convert


SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def authenticate():
    """Authenticate and return Google Drive service."""
    creds = None

    # Load existing credentials from token.json if available
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def list_files_in_folder(service, folder_id):
    """List all files in a Google Drive folder."""
    query = f"'{folder_id}' in parents and trashed = false"
    results = (
        service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    )
    items = results.get("files", [])
    return items


def download_files_as_pdf(service, files, folder_path="downloads"):
    """Download Google Drive files as PDFs."""
    # Create downloads folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for item in files:
        file_id = item["id"]
        file_name = item["name"]
        mime_type = item["mimeType"]

        # Determine if file can be exported as PDF
        if mime_type == "application/vnd.google-apps.document":
            export_mime = "application/pdf"
            file_path = os.path.join(folder_path, f"{file_name}.pdf")
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
        elif mime_type == "application/vnd.google-apps.spreadsheet":
            export_mime = "application/pdf"
            file_path = os.path.join(folder_path, f"{file_name}.pdf")
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
        elif mime_type == "application/vnd.google-apps.presentation":
            export_mime = "application/pdf"
            file_path = os.path.join(folder_path, f"{file_name}.pdf")
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
        elif mime_type == "application/pdf":
            # Already a PDF, download directly
            request = service.files().get_media(fileId=file_id)
            file_path = os.path.join(folder_path, f"{file_name}")
            if not file_path.endswith(".pdf"):
                file_path += ".pdf"
        elif (
            mime_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            # DOCX file - download and convert using LibreOffice
            file_path = os.path.join(folder_path, f"{file_name}")
            if not file_path.endswith(".docx"):
                file_path += ".docx"

            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(file_path, "wb")
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Convert to PDF using LibreOffice
            # file_path = os.path.join(folder_path, f"{file_name}.pdf")
            # os.system(
            #     f'podman exec doconvert "soffice --headless --convert-to pdf --outdir /docs \\"/docs/temp/{file_name}\\""'
            # )
            # os.remove(temp_file)
            # print(f"Downloaded and converted: {file_name}.pdf")
            print(f"Downloaded: {file_name}")
            continue
        elif (
            mime_type
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            # XLSX file - download and convert using LibreOffice
            file_path = os.path.join(folder_path, f"{file_name}")
            if not file_path.endswith(".xlsx"):
                file_path += ".xlsx"

            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(file_path, "wb")
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Convert to PDF using LibreOffice
            # file_path = os.path.join(folder_path, f"{file_name}.pdf")
            # os.system(
            #     f'podman exec doconvert "soffice --headless --convert-to pdf --outdir /docs \\"/docs/temp/{file_name}\\""'
            # )
            # os.remove(temp_file)
            # print(f"Downloaded and converted: {file_name}.pdf")
            print(f"Downloaded: {file_name}")
            continue
        elif (
            mime_type
            == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ):
            # PPTX file - download and convert using LibreOffice
            folder_path = os.path.join(folder_path, f"{file_name}")
            if not folder_path.endswith(".pptx"):
                folder_path += ".pptx"

            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(folder_path, "wb")
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Convert to PDF using LibreOffice
            # file_path = os.path.join(folder_path, f"{file_name}.pdf")
            # os.system(
            #     f'podman exec doconvert "soffice --headless --convert-to pdf --outdir /docs/ \\"/docs/temp/{file_name}\\""'
            # )
            # os.remove(temp_file)
            # print(f"Downloaded and converted: {file_name}.pdf")
            print(f"Downloaded: {file_name}")
            continue
        else:
            print(f"Skipping {file_name} - unsupported type: {mime_type}")
            continue

        # Download the file
        fh = io.FileIO(file_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Downloaded: {file_name}.pdf ({int(status.progress() * 100)}%)")


def main():
    folder_id = input("Enter Google Drive folder ID: ").strip()
    if not folder_id:
        folder_id = "your_folder_id_here"  # Replace with your actual folder ID

    service = authenticate()
    print(f"Listing files in folder: {folder_id}")
    files = list_files_in_folder(service, folder_id)

    if not files:
        return

    print(f"Found {len(files)} files. Starting download...")
    download_files_as_pdf(service, files)
    print("Download complete!")


if __name__ == "__main__":
    main()
