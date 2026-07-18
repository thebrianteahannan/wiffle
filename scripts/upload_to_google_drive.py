#!/usr/bin/env python3
"""Upload a file to Google Drive using the injected OAuth secret."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def load_credentials() -> Credentials:
    raw = os.environ.get("Google Drive")
    if not raw:
        raise SystemExit("Missing 'Google Drive' environment secret")
    info = json.loads(raw)
    # Refresh without requesting new scopes; token was issued with existing grants.
    creds = Credentials.from_authorized_user_info(info)
    if not creds.valid:
        creds.refresh(Request())
    return creds


def upload(path: Path, name: str | None = None) -> dict:
    path = path.resolve()
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    creds = load_credentials()
    service = build("drive", "v3", credentials=creds, cache_discovery=False)

    metadata = {
        "name": name or path.name,
        "mimeType": "application/pdf",
    }
    media = MediaFileUpload(str(path), mimetype="application/pdf", resumable=True)
    created = (
        service.files()
        .create(body=metadata, media_body=media, fields="id,name,webViewLink,webContentLink")
        .execute()
    )

    # Anyone with the link can view (convenient share link for the user).
    service.permissions().create(
        fileId=created["id"],
        body={"type": "anyone", "role": "reader"},
        fields="id",
    ).execute()

    # Re-fetch links after permission change.
    final = (
        service.files()
        .get(fileId=created["id"], fields="id,name,webViewLink,webContentLink")
        .execute()
    )
    return final


if __name__ == "__main__":
    pdf = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/Wiffle_Ball_Pitching_Strategies.pdf")
    result = upload(pdf)
    print(json.dumps(result, indent=2))
