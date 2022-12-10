from __future__ import print_function

import os.path
import io
import shutil

from Credentials import Credential
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from dotenv import load_dotenv

load_dotenv()
folder_id = os.getenv('FOLDER_ID')

def GetFiles(folder_id):
    creds = Credential.GetCredentials()

    try:
        service = build('drive', 'v3', credentials=creds)

        results = service.files().list(q=f"'{folder_id}' in parents",
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                   'files(id, name)',
                                            pageToken=None).execute()
        
        items = results.get('files', [])
        
        print(f'Files count: {len(items)}')
        
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    
    except HttpError as error:
        raise error

    return items

def DownloadFile(file, cleanupBeforeDownloading = True):
    if cleanupBeforeDownloading:
        PreDownloadCleanup()

    if not os.path.exists("Downloads"):
        os.makedirs('Downloads')

    creds = Credential.GetCredentials()

    try:
        service = build('drive', 'v3', credentials=creds)

        file_name = file['name']
        file_id = file['id']

        request = service.files().get_media(fileId=file_id)
        target_file = io.FileIO(os.path.join('Downloads', f'{file_name}'), mode='wb')
        downloader = MediaIoBaseDownload(target_file, request)
        done = False
        
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')
            download_destination = file_name

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return download_destination

def PreDownloadCleanup(folder = "Downloads"):
    shutil.rmtree(folder, ignore_errors=True)

if __name__ == '__main__':
    items = GetFiles(folder_id)

    for item in items:
        DownloadFile(item)
