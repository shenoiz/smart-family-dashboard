from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import io
import os
import schedule
import time

from config import GOOGLE_DRIVE_FOLDER_ID, PHOTOS_DIR, PHOTO_REFRESH_HOURS

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CREDS_FILE = "credentials.json"  # Downloaded from Google Cloud Console


def sync_photos():
    print("Syncing photos from Google Drive...")
    os.makedirs(PHOTOS_DIR, exist_ok=True)

    try:
        creds = service_account.Credentials.from_service_account_file(
            CREDS_FILE, scopes=SCOPES
        )

        service = build("drive", "v3", credentials=creds)

        results = (
            service.files()
            .list(
                q=f"'{GOOGLE_DRIVE_FOLDER_ID}' in parents and mimeType contains 'image/'",
                fields="files(id, name)",
            )
            .execute()
        )

        for f in results.get("files", []):
            dest = os.path.join(PHOTOS_DIR, f["name"])

            if os.path.exists(dest):
                continue  # already downloaded

            req = service.files().get_media(fileId=f["id"])
            buf = io.BytesIO()
            dl = MediaIoBaseDownload(buf, req)

            done = False
            while not done:
                _, done = dl.next_chunk()

            with open(dest, "wb") as out:
                out.write(buf.getvalue())

            print(f' Downloaded: {f["name"]}')

        print("Sync complete.")

    except Exception as e:
        print(f"Drive sync error: {e}")


def start():
    sync_photos()

    schedule.every(PHOTO_REFRESH_HOURS).hours.do(sync_photos)

    while True:
        schedule.run_pending()
        time.sleep(60)
