from time import sleep
from datetime import datetime, time
from typing import List, Set
from re import search
from os import getenv

from googleapiclient.discovery import Resource, build
from gspread import client, authorize, models
from oauth2client.service_account import ServiceAccountCredentials

from video import Video

def get_youtube_client() -> Resource:
    name = 'youtube'
    version = 'v3'
    key = getenv('youtube_key')

    youtube_auth = build(name, version, developerKey=key)
    return youtube_auth

def get_sheet_client() -> client.Client:
    scopes = (
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive'
        )

    secret = {
        "type": getenv('type'),
        "project_id": getenv('project_id'),
        "private_key_id": getenv("private_key_id"),
        "private_key": getenv('private_key'),
        "client_email": getenv('client_email'),
        "client_id": getenv('client_id'),
        "auth_uri": getenv('auth_uri'),
        "token_uri": getenv('token_uri'),
        "auth_provider_x509_cert_url": getenv('auth_provider_x509_cert_url'),
        "client_x509_cert_url": getenv('client_x')
        }
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(secret, scopes)
    sheet_client = authorize(credentials)

    return sheet_client

def open_sheet(
    client: client.Client, 
    name: str, 
    worksheet_index: int) -> models.Worksheet:
    return client.open(name).get_worksheet(worksheet_index)

def pt_to_iso(pt: str) -> str:
    hour = search('([0-9][0-9]?)(?=H)', pt)
    hour = hour.group(0).zfill(2) if hour else '00'

    minute = search('([0-9][0-9]?)(?=M)', pt)
    minute = minute.group(0).zfill(2) if minute else '00'

    second = search('([0-9][0-9]?)(?=S)', pt)
    second = second.group(0).zfill(2) if second else '00'

    return f'{hour}:{minute}:{second}'

def filter_video(
    client: Resource,  
    seen: Set[str], 
    current_page_item: List) -> List[Video]:
    filtered = []

    print('Filtering duplicate videos.')
    for video_data in current_page_item:
        video_id  = video_data['snippet']['resourceId']['videoId']

        if video_id in seen:
            continue

        seen.add(video_id)
        snippet = video_data['snippet']
        title = snippet['title']
        addded_to_playlist_dt = datetime.strptime(
            snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'
            )

        more_data = client.videos().list(
                        part='snippet, contentDetails',
                        id=video_id
                        ).execute()

        if not more_data['items']:
            continue

        more_snippet = more_data['items'][0]['snippet']
        uploader_name = more_snippet['channelTitle']
        uploader_id = more_snippet['channelId']
        uploaded_dt = datetime.strptime(
                        more_snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'
                        )

        duration = time.fromisoformat(
                    pt_to_iso(more_data['items'][0]['contentDetails']['duration'])
                    )
        
        new_video = Video(
            video_id, 
            title, 
            addded_to_playlist_dt, 
            uploaded_dt, 
            uploader_name, 
            uploader_id, 
            duration)

        filtered.append(new_video)
        
    print("Filering finished for token.")
    return filtered

def get_videos(
    client: Resource, 
    playlist_id: str,  
    seen: Set[str],
    max_result_per_page: int = 50) -> List[Video]:

    videos_unseen = []
    next_page_token = ''
    while True:
        print(f'Fetching with token: {next_page_token}.')
        request = client.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=max_result_per_page,
            pageToken=next_page_token
            )

        current_page: dict = request.execute()
        next_page_token = current_page.get('nextPageToken', '')
        if not next_page_token:
            print('Fetching complete.')
            return videos_unseen

        current_page_item = current_page.get('items')
        videos_unseen.extend(filter_video(client, seen, current_page_item))
            
def task():
    sheet_name = getenv('sheet_name')
    playlist_id = getenv('playlist_id')
    youtube_client = get_youtube_client()
    
    sheet_client = get_sheet_client()
    sheet_opened = open_sheet(sheet_client, sheet_name, 2)

    while True:
        print('Working.')
        seen = set(sheet_opened.col_values(6))
        unseen = get_videos(youtube_client, playlist_id, seen)

        for video in unseen:
            package = video.prepare_export()

            print(f'Adding {package[2].rstrip()}.')
            sheet_opened.insert_row(package, 2)
            sleep(6)
        print("Finished for the day.")
        sleep(24*60*60)

def main():
    print('Running')
    task()

if __name__ == '__main__':
    main()
