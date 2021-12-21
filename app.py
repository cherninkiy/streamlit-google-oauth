import os.path
import pickle
from io import BytesIO
import streamlit as st
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_gdrive_file_list(folder_id):
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
            # flow = InstalledAppFlow.from_client_secrets_file(
            #     "../../service-account.json", SCOPES)
            # creds = flow.run_local_server(port=9080)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("drive", "v3", credentials=creds)

    result = service.files() \
        .list(
            q=f'"{folder_id}" in parents',
            pageSize=400,
            fields="files(id, name)"
        ) \
        .execute()

    files = result.get("files")

    return files


def load_gdrive_file_data(file_id):
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "../../service-account.json", SCOPES)
            creds = flow.run_local_server(port=9080)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("drive", "v3", credentials=creds)

    request = service.files().get_media(fileId=file_id)
    buffer = BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

    if done:
        buffer.seek(0)
        return buffer

    return None

st.write(get_gdrive_file_list("12rmMvI9YfS1eF-KXmoftQjTxo4JigZgB"))