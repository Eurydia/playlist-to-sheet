from time import sleep
from re import search

import googleapiclient.discovery
import googleapiclient.errors

import gspread
import oauth2client.service_account

class Video:
    def __init__(self, given_id, title, date_added, auth):
        self.authorize = auth

        self.id = given_id
        self.title = title
        self.date_added = date_added

        self.url = f'https://www.youtube.com/watch?v={self.id}'

        self.date_uploaded = None
        self.uploader = None
        self.uploader_id = None
        self.duration = None


    def request_extra_info(self):
        extra_request = self.authorize.videos().list(
                part='snippet, contentDetails',
                id=self.id)

        item_extra = extra_request.execute()

        return item_extra


    def format_duration(self, duration):
        unformatted = duration
        hour = '00'
        minute = '00'
        second = '00'
        
        if 'H' in duration:
            hour = search('(\d{1,2})(?=H)', unformatted).group(0)
            if len(hour) < 2:
                hour = f'0{hour}'

        if 'M' in duration:
            minute = search('(\d{1,2})(?=M)', unformatted).group(0)
            if len(minute) < 2:
                minute = f'0{minute}'

        if 'S' in duration:
            second = search('(\d{1,2})(?=S)', unformatted).group(0)
            if len(second) < 2:
                second = f'0{second}'

        formatted = f'{hour}:{minute}:{second}'
        return formatted
    
    
    def format_date(self, date):
        date = date.replace('-', '/')
        date = date.replace('T', ' ')
        date = date.replace('Z', ' ')
        return date

    def export(self):
        package = [
            self.date_added,
            self.uploader,
            self.title,
            self.duration,
            self.url,
            self.id,
            self.uploader_id,
            self.date_uploaded
        ]
        return package


def getYoutubeAuth():
    key = 'AIzaSyAm0Lm-JL3tx70Kj9umCqVqHLca7NNrH-A'
    nameAPI = 'youtube'
    versionAPI = 'v3'

    youtubeAuth = googleapiclient.discovery.build(nameAPI, versionAPI, developerKey=key)

    return youtubeAuth


def getSheetClient():
    scopesAPI = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive.file',
                    'https://www.googleapis.com/auth/drive']

    secret = {
        "type": "service_account",
        "project_id": "songs-playlist-299413",
        "private_key_id": "ffb65a73053f6f3cb200b46bc4eed09854c363c3",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDZOaklYVWHIVn9\nvVMJ0QpBGQPdDtDmuPKn0+lxXs4PeisvYBKOIpaaxnVteLHMAuqd8IOS1cvwjzEY\noEXMQGZRjy7gO8BeCbGMqJaMt7UwSVwHE3tnEPCza6jy/UFyTwI5BNoLQr0gu90f\nMaB/4iBZeMtXnD8s1uAl7z2oNZsyoia2wKRmaV3qpcJRwIqP4L3lFBo3JYAMTTq3\ne/rW+9d0cgisoZbeUB32/Re5kkyME8fgOKFYVFUyRJ3SAapFK+FUHx4EFuhZRahW\nibK62kdbRnWx78aXrFDufYRBEQszIC9TQ4UTunX5rbyMXEPHMly/yb7DAq/QMNdV\nSglJQ5nLAgMBAAECggEAEEGU63O3y1ePHQKUmsj2i/2bwOjRcFrJ6g5dS3stT5I0\ndiSp7tIe1DFi61DbeWmEdlJf/laanwOQSIgCATGWlqbw+p3uHPt7uouJTLmYySbM\nSMlH9GQbp0m4yIp0YeIQyASZbrtNXQxCFYoIuVlKU3fLO+C5B5mDB8O6KQLt/OFr\nQMNWivZJP20QTiBUG5bGDtyFTzOLzCZFFmLjB+qiMSL0DPUMStPRC+ytIEboI3Gx\nxHrlK/vl/P4eDct7yINwT9NzSgmdO8JMWfMlO70jfFrR5x5hczQENsPOB6ClyzDt\n2Q69nNZyzet+Vh3uf09kBbL1Xm/SENTt5IWaUwahiQKBgQD99yZ6x/K/2DDqzqqu\no9m/0IwZrB+LsaFwNM6BAXCPO+7IcItYAMmD0dE0BUYxtBSrj4QkuTK5VFgYaVbL\nlM1EKDJqgHZzoNhUJopvsOt5qSRTelecQnBylHnfaaY5bv5i94AwwtlQ+fPJCu3u\nOLlIV8znwRPvcRY1ttGg+okXSQKBgQDa9yk+nNP8pFSmfTt7GdYaNRJrZ517e15y\n6nJQoon/ZFMQN9qSSFdYJ9kTi5T56kzffybeVzNAvJcz6Grl/yY5aMx2reKgppmj\naNb7e5kwUoTFwOI6sTuV90Gw0v9S6OtUJkhYLKbOl/7WenLej5neP0ZobwpdDw9s\nYXPLyckEcwKBgAWWhJA7CgpSlXD1Lyg8jrP7wLln4iHOvMCdSNXp1DIynWRnpYlA\nKy7tVO8SFqNNVQ8ZT00HjigpxO50kuZT1dhkEgfp37FXnqrrVixy9httL1Fu5bKY\ne6Tpw2y5BGFLIenHjFiGUQXJGiYYSXfuY5VF6UpII0oncNepuB8UpCORAoGBAK+Z\n87vA7cj4yOJUIHWSvL97vG/iQsuanp4uIstD7sOgY3ToNiOGXHXYTyB7mlfqbQf3\n4uYArJvIIsKAK+qTesYjo4Wx4cPQl/oSxAYekzXLl6s4CrXjGNQl3MrAC/8jyEZO\nBUqhVIzuHHNI9AJEy7MOr5plIryKrWXPqZvPEaS9AoGAEDUmMqav6MB5IIcOoIuV\nlXCwsraveFv9aZ3ZZ+fbhM1a0VuRNwaJk6lpgl8GvF+XlVdI2Ug44olVbvHRDy0b\nFI+2a+DVSw0g4rxLz5HGr6oHghhJUB2VXRCD2WW1+ZVOvf6QUZ9zRj12Qds/Qjzw\n7r4wfUKywiN+bAW1s4KLu90=\n-----END PRIVATE KEY-----\n",
        "client_email": "updater@songs-playlist-299413.iam.gserviceaccount.com",
        "client_id": "111288946341559365686",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/updater%40songs-playlist-299413.iam.gserviceaccount.com"
        }

    credentials = oauth2client.service_account.ServiceAccountCredentials.from_json_keyfile_dict(secret, scopesAPI)
    sheetClient = gspread.authorize(credentials)

    return sheetClient


def request_playlist(playlist_object, playlist_id, token, max_result_per_page):
    
    request = playlist_object.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=max_result_per_page,
        pageToken=token)

    return request.execute()


def main():
    playlist_auth = getYoutubeAuth()
    sheet_client_opened = getSheetClient().open('Favorite songs').get_worksheet(2)

    playlist_id = 'PLy6awrEBaGlOUQHA46oukOQ75esob8ZEM'
    next_page_token = None
    items_per_page = 50

    while True:

        #This object store requested playlist data
        playlist = request_playlist(playlist_auth, playlist_id, next_page_token, items_per_page)

        playlist_items = playlist['items']
        
        for items in playlist_items:

            # Store video ID from Sheet
            existing_id = sheet_client_opened.col_values(6)

            item_id = items['snippet']['resourceId']['videoId']

            if not item_id in existing_id:

                item_title = items['snippet']['title']
                item_added_to_playlist = items['snippet']['publishedAt']

                #initiate object
                current_video = Video(item_id, item_title, item_added_to_playlist, playlist_auth)

                #format date added
                current_video.date_added = current_video.format_date(current_video.date_added)

                #requesting more information
                current_video_extra = current_video.request_extra_info()

                #formatting duration
                duration = current_video_extra['items'][0]['contentDetails']['duration']
                current_video.duration = current_video.format_duration(duration)

                #format date uploaded
                date_uploaded = current_video_extra['items'][0]['snippet']['publishedAt']
                current_video.date_uploaded = current_video.format_date(date_uploaded)

                #getting channel title
                uploader = current_video_extra['items'][0]['snippet']['channelTitle']
                current_video.uploader = uploader

                #getting channel id
                uploader_id = current_video_extra['items'][0]['snippet']['channelId']
                current_video.uploader_id = uploader_id

                package = current_video.export()
                
                sheet_client_opened.insert_row(package, 2)
                sleep(5)

            else:
                print('already exist in database')
            
        next_page_token = playlist.get('nextPageToken', None)

        if next_page_token == None:
            print('Finished')
            break

        sleep(5)

while True:
        
    print('Working')

    main()

    print('Finished')

    sleep(60*60)
