#!/usr/bin/env python3
"""Upload tournament PDF to Google Drive and make it shareable."""

import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

PDF = Path("/opt/cursor/artifacts/Wizards_of_Wiffs_PLW_Tournament_Aug1_2026.pdf")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def main():
    raw = os.environ["Google Drive"]
    data = json.loads(raw)
    # authorized_user format from google-auth-oauthlib
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes") or SCOPES,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build("drive", "v3", credentials=creds, cache_discovery=False)

    meta = {
        "name": "Wizards_of_Wiffs_PLW_Tournament_Aug1_2026.pdf",
        "mimeType": "application/pdf",
    }
    media = MediaFileUpload(str(PDF), mimetype="application/pdf", resumable=True)
    created = (
        service.files()
        .create(body=meta, media_body=media, fields="id,name,webViewLink,webContentLink")
        .execute()
    )
    file_id = created["id"]
    print("Created:", created)

    # Anyone with the link can view
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
        fields="id",
    ).execute()

    updated = (
        service.files()
        .get(fileId=file_id, fields="id,name,webViewLink,webContentLink")
        .execute()
    )
    print("SHARE_LINK:", updated.get("webViewLink"))
    print("DOWNLOAD_LINK:", updated.get("webContentLink"))
    print("FILE_ID:", file_id)


if __name__ == "__main__":
    main()
