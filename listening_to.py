import json
import spotipy
from datetime import datetime
import webbrowser
from spotipy import oauth2
from spotipy import SpotifyException

import tweepy
import time

import creds

#python creds
SPOTIPY_CLIENT_ID = creds.SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET = creds.SPOTIPY_CLIENT_SECRET
SPOTIPY_REDIRECT_URI = creds.SPOTIPY_REDIRECT_URI
SPOTIPY_CACHE = creds.SPOTIPY_CACHE

#twitter
#creds
consumer_key = creds.consumer_key
consumer_secret = creds.consumer_secret
access_token = creds.access_token
access_secret = creds.access_secret


#login for twitter
auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_secret)
auth.secure = True
api = tweepy.API(auth)

#spotify
#currently playing scope
scope = 'user-read-currently-playing'
#your username
username = 'jerryxue1600'

#authtoken
sp_oauth = oauth2.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,client_secret=SPOTIPY_CLIENT_SECRET,redirect_uri=SPOTIPY_REDIRECT_URI,scope=scope,cache_path=SPOTIPY_CACHE)
token_info = sp_oauth.get_cached_token()

if not token_info:
    auth_url = sp_oauth.get_authorize_url(show_dialog=True)
    #print(auth_url)
    webbrowser.open(auth_url)
    response = input('Paste the redirect url here: ')
    code = sp_oauth.parse_response_code(response)
    token_info = sp_oauth.get_access_token(code)
    token = token_info['access_token']
    spotifyObject  = spotipy.Spotify(auth=token)
else:
    token = token_info['access_token']
    spotifyObject  = spotipy.Spotify(auth=token)


#using ur refresh token to request a new access token
def refresh_your_access():
    global token_info, spotifyObject
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        token = token_info['access_token']
        spotifyObject = spotipy.Spotify(auth=token)

id="";

def main():
    global id, api
    current_track = spotifyObject.current_user_playing_track()
    isp = current_track["is_playing"]
    #only run this loop when the song is different from your last song
    if (isp == True and id != current_track["item"]["id"]):
        #id is what your are listening to
        id = current_track["item"]["id"]
        for x in range(0, 20):
            current_track = spotifyObject.current_user_playing_track()
            time.sleep(1)
            #check if you switched songs
            if id != current_track["item"]["id"] or current_track["is_playing"] == False :
                #if you switched songs break the for loop
                break
            if x == 19: #last loop, 5 sec passed
                songname = current_track["item"]["name"]
                artistname = current_track["item"]["artists"][0]["name"]
                datetime.now().strftime('%Y-%m-%d %H:%M:%S');
                api.update_status("Jerry is currently listening to \"" + songname + "\" by " + artistname + " at " + datetime.now().strftime('%I:%M %p'))
    else:
        #it's the same song, give it a 10 seconds
        time.sleep(10)

if __name__ == '__main__':
    while (True):
        try:
            main()
        except tweepy.error.TweepError:
            #you probaby duplicated ur tweet or you had a super long song name with artist
            time.sleep(30)
        except SpotifyException:
            #ur token expired
            refresh_your_access()
        except Exception as e:
            #the program is probably tired of ur loop because its the same song
            #or your spotifyobject isnt working properly.
            print(e)
            refresh_your_access()
            time.sleep(60)
        if not spotifyObject.current_user_playing_track()["is_playing"]:
            break;
