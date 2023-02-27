# Script Name: Download YouTube Playlist as MP3
# Author: hearbrckAcdmy
# Description: A script to download a YouTube playlist as MP3 files.
# Version: 1.0
# Last Updated: February 25, 2023

import os
import subprocess
import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up Google API credentials
creds, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/youtube.force-ssl'])
youtube = build('youtube', 'v3', credentials=creds)

# Get the playlist URL
playlist_url = input("Enter the URL of the YouTube playlist: ")

# Get the list of video IDs in the playlist
playlist_id = playlist_url.split('list=')[1]
try:
    playlist_response = youtube.playlistItems().list(
        playlistId=playlist_id,
        part='snippet',
        maxResults=50
    ).execute()
except HttpError as e:
    print(f"An error occurred: {e}")
    exit()

# Ask the user where to save the files
if os.name == 'nt':
    # On Windows, open the file explorer window to prompt the user for a directory
    import ctypes
    from ctypes.wintypes import MAX_PATH

    # Define Win32 API functions
    CSIDL_PERSONAL = 5       # My Documents folder
    SHGFP_TYPE_CURRENT = 0   # Get the current, not default, folder path
    shell32 = ctypes.windll.shell32
    buf = ctypes.create_unicode_buffer(MAX_PATH)

    # Get the current user's My Documents folder path
    shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

    # Open the file explorer window to prompt the user for a directory
    ctypes.windll.user32.MessageBoxW(None, "Choose the directory to save the mp3 files in.", "Select Directory", 0)
    output_dir = ctypes.windll.shell32.SHBrowseForFolderW(None, "Select Directory", 0, buf, 0, None)
    if output_dir:
        output_dir = os.path.abspath(output_dir)
    else:
        print("No directory selected.")
        exit()
else:
    # On non-Windows platforms, prompt the user to enter a directory manually
    output_dir = input("Enter the directory to save the mp3 files in: ")

if not os.path.isdir(output_dir):
    print("Invalid directory specified.")
    exit()

# Create a folder for the playlist
playlist_title = playlist_response['items'][0]['snippet']['playlistTitle']
playlist_dir = os.path.join(output_dir, playlist_title)
if not os.path.exists(playlist_dir):
    os.makedirs(playlist_dir)

# Download each video as an mp3 file
for item in playlist_response['items']:
    video_id = item['snippet']['resourceId']['videoId']
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    video_title = item['snippet']['title']
    output_filename = f"{playlist_title}/{video_title}.mp3"
    try:
        subprocess.run(["youtube-dl", "-x", "--audio-format", "mp3", "-o", output_filename, video_url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while downloading {video_title}: {e}")
