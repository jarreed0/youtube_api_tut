import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from PIL import Image, ImageDraw, ImageFont

VID_ID = 'YOUR_VIDEO_ID'

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def create_thumb(view_count, kind):
    # Create a 1280x720 image with a red background
    #image = Image.new('RGB', (1280, 720), color='red')
    image = Image.new('RGB', (1280, 720), color='#1E2021')
    # Draw the view count in yellow at the center of the image
    draw = ImageDraw.Draw(image)
    text = f'{view_count}\n{kind}'
    font = ImageFont.truetype('Roboto.ttf', size=240)
    text_width, text_height = draw.textsize(text, font=font)
    x = (1280 - text_width) / 2
    y = (720 - text_height) / 3
    draw.text((x, y), text, fill='white', font=font)
    #draw.text((x, y), text, fill='yellow', font=font)
    name = 'genthumb.png'
    image.save(name, format='JPEG')
    return name

def yt_check():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'your_client_secret.json', SCOPES)
                #'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def update(vid_id, thumb, title):
    creds = yt_check()

    # Call the YouTube API to upload the thumbnail
    try:
         youtube = build('youtube', 'v3', credentials=creds)
         youtube.thumbnails().set(
             videoId=vid_id,
             media_body=thumb
         ).execute()
         print('The thumbnail was successfully uploaded.')
         videos_list_response = youtube.videos().list(
              id = vid_id,
              part = 'snippet'
         ).execute()
         videos_list_snippet = videos_list_response['items'][0]['snippet']
         videos_list_snippet['title'] = title
         response = youtube.videos().update(
              part = 'snippet',
              body = dict(
                   snippet = videos_list_snippet,
                   id = vid_id
         )).execute()
         print(f'Updated video title: {response["snippet"]["title"]}')
    except HttpError as error:
         print('An error occurred: %s' % error)

def count_check(video_id, kind):
    creds = yt_check()

    try:
         youtube = build('youtube', 'v3', credentials=creds)
         # Call the API to retrieve the video statistics
         video_response = youtube.videos().list(
              part='statistics',
              id=video_id
         ).execute()
         # Get the view count from the response
         view_count = video_response['items'][0]['statistics'][kind]
         print(video_response)
         print(video_response['items'])
         # Print the view count
         print(f'The video with ID "{video_id}" has {view_count} {kind}.')
         return view_count
    except HttpError as error:
         print('An error occurred: %s' % error)

mode = 1

# viewCount, VIEWS
if mode == 1:
 count = count_check(VID_ID, "viewCount")
 thumb = create_thumb(count, "VIEWS")
 update(VID_ID, thumb, f'This Video Has {count} Views')
# likeCount, LIKES
if mode == 2:
 count = count_check(VID_ID, "likeCount")
 thumb = create_thumb(count, "LIKES")
 update(VID_ID, thumb, f'This Video Has {count} Likes')
# dislikeCount, DISLIKES
if mode == 3:
 count = count_check(VID_ID, "dislikeCount")
 thumb = create_thumb(count, "DISLIKES")
 update(VID_ID, thumb, f'This Video Has {count} Dislikes')
# commentCount, COMMENTS
if mode == 4:
 count = count_check(VID_ID, "commentCount")
 thumb = create_thumb(count, "COMMENTS")
 update(VID_ID, thumb, f'This Video Has {count} Comments')
