import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from secret import *


REDIRECT_URI = 'http://localhost:8080'


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope='playlist-modify-private'))

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def extract_artist(title, description):
    artist = "Unknown"
    if "-" in title:
        artist = title.split("-")[0].strip()
    elif "by" in description.lower():
        artist = description.split("by")[1].split()[0].strip()
    return artist

def create_playlist(name, description=''):
    playlist = sp.user_playlist_create(sp.me()['id'], name, public=False, description=description)
    return playlist['id']

def add_tracks_to_playlist(playlist_id, track_uris):
    sp.playlist_add_items(playlist_id, track_uris)

def search_track(query):
    results = sp.search(q=query, limit=1)
    if results['tracks']['items']:
        return results['tracks']['items'][0]['uri']
    else:
        return None

def main():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"


    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.videos().list(
        part="snippet,contentDetails",
        maxResults=25,
        myRating="like"
    )
    response = request.execute()


    playlist_name = "Liked from YouTube"  
    playlist_id = create_playlist(playlist_name)
    track_uris = []


    for item in response['items']:
        video_title = item['snippet']['title']
        description = item['snippet']['description']

        if 'music' in description.lower() or 'music' in video_title.lower():

            artist = extract_artist(video_title, description)
            print("Video Title:", video_title)
            print("Artist:", artist)


            track_uri = search_track(f"{video_title} {artist}")


            if track_uri:
                track_uris.append(track_uri)
                print("Song added to playlist.")
            else:
                print("Song not found on Spotify.")


    if track_uris:
        add_tracks_to_playlist(playlist_id, track_uris)
        print("All songs added to the playlist.")
    else:
        print("No songs found to add to the playlist.")

if __name__ == "__main__":
    main()
