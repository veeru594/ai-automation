# drive_uploader.py
import os
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger("drive_uploader")

class DriveUploadError(Exception):
    pass

class DriveUploader:
    def __init__(self, credentials_json_path="credentials.json", scopes=None):
        scopes = scopes or ["https://www.googleapis.com/auth/drive"]
        if not os.path.exists(credentials_json_path):
            raise DriveUploadError("credentials_json_missing")
        creds = service_account.Credentials.from_service_account_file(credentials_json_path, scopes=scopes)
        self.service = build('drive', 'v3', credentials=creds)

    def upload_file(self, local_path, filename=None, folder_id=None):
        filename = filename or local_path.split("/")[-1]
        file_metadata = {"name": filename}
        if folder_id:
            file_metadata["parents"] = [folder_id]
        media = MediaFileUpload(local_path, mimetype="image/png", resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields="id,webViewLink").execute()
        file_id = file.get("id")
        web_view_link = file.get("webViewLink")
        # optionally set file permission to anyone with link (if you want public URLs)
        try:
            self.service.permissions().create(fileId=file_id, body={"type": "anyone", "role": "reader"}).execute()
            # then build a direct download or view link
        except Exception:
            logger.warning("Could not set file public; continuing")
        return file_id, web_view_link
