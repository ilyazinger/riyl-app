import requests
import base64
import random
import string
import urllib.parse
from get_token import get_token

#Using Spotify's Client Credentials Authorization Flow

CLIENT_ID = '5e3b178d331d4a239bd30375ad348520'
CLIENT_SECRET = 'ab3dadd7968f4e6a823c2a7059da47c5'
REDIRECT_URI = 'http://localhost:5000/callback' 

AUTH_URL = 'https://accounts.spotify.com/authorize' #Authorize Endpoint
TOKEN_URL = 'https://accounts.spotify.com/api/token' #Token Endpoint, use POST
API_BASE_URL = 'https://api.spotify.com/v1/'

REC_ENDPOINT = 'https://api.spotify.com/v1/recommendations?'
ALBUM_ENDPOINT = 'https://api.spotify.com/v1/albums/'
TRACKS_ENDPOINT = 'https://api.spotify.com/v1/tracks/'
AUDIO_FEATS_ENDPOINT = 'https://api.spotify.com/v1/audio-features/'
SEARCH_ENDPOINT = 'https://api.spotify.com/v1/search?'

#######################
## HELPER FUNCTIONS ###
#######################
def b64_encode(s):
    return base64.b64encode(s.encode()).decode()

def decode(s):
    return base64.b64decode(s).decode()

def authorize():
    #TODO remove or change authorization flow, right now it's Client Credentials and there's no need for a user to give authorization
    #GET to the AUTH_URL
    params = {
        'client_id' : CLIENT_ID,
        'response_type': 'code',
        'redirect_uri' : REDIRECT_URI,
        'state' : ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16)),
        'show_dialog' : False
    }

    #gets authorization code for token
    get_response = requests.get(AUTH_URL, params=params)
    print(get_response.url)

def get_album(uri, headers):
    #TODO add album input or search feature
    return requests.get(ALBUM_ENDPOINT+uri, headers=headers)

def get_artist():
    ...

def get_track():
    #TODO function gets track using TRACKS_ENDPOINT, instead of putting this in main
    ...

def get_audio_features():
    #TODO function gets audio features from a track using AUDIO_FEATS_ENDPOINT, instead of putting this in main
    ...

def response_debug(r):
    query = r.iter_lines(decode_unicode=True) #prints out entire Response object in readable format (optional)
    for _ in query:
        print(_,end='\n')

def search(query):
    #TODO create a simple search function, maybe one that takes only an album, artist or track?
    #likely returns the album URI?

    headers = {
        "Authorization" : "Bearer " + get_token().json()['access_token'] #Authorization header to pass in to various end points
    }

    limit = 10
    s_query = urllib.parse.quote_plus(f'q={query}&type=album&limit={limit}', safe="=&")
    r = requests.get(url=f'{SEARCH_ENDPOINT}{s_query}', headers=headers)
    return r

def rec_albums():
    ...

#################
##  MAIN LOGIC ##
#################

def main():
    
    #HEADERS
    headers = {
        "Authorization" : "Bearer " + get_token().json()['access_token'] #Authorization header to pass in to various end points
    }
    
    try:
        s = search(input("Album name: ")) #Accept an album title, can also accept artist and album title or whatever Spotify's Search API can accept

        searched_albums = s.json()['albums']['items'] #list of albums as list of dicts
        searched_album_ids = [a['id'] for a in s.json()['albums']['items']] #list of album ids as list of strings

        index = 1
        for a in searched_albums: #loop through dicts of albums, search() limits to 10 searches currently, print Artist(s) - Album
            print(f"{index}. ", end="")
            for b in range(0,len(a['artists'])):
                if len(a['artists']) > 1:
                    print(f"{a['artists'][b]['name']}",end=" # ")
                else:
                    print(f"{a['artists'][b]['name']}",end="")
            print(f" - {a['name']}")
            index += 1
        try:
            r = get_album(searched_album_ids[int(input("Please choose an album from 1 to 10: ")) - 1],headers)
            #TODO possibly create a get_tracklist function?
            tracklist = [r.json()['tracks']['items'][_]['id'] for _ in range(0,r.json()['tracks']['total'])] #list of tracks IDs from album
            #TODO possibly create a get artist_id function?
            artist_id = r.json()['artists'][0]['id']
            
            limit = 5
            #seed_tracks are limited to two, should be least popular and most popular, need function to set the two and add in params
            params = f"limit={limit}&seed_artists={artist_id}&seed_tracks={tracklist[0]}" #params to be passed into the Recommendation GET Request, limit to 10 recommendations

            #TODO mechanism for how/what we want to seed to the recommendation engine to provide us 10 album recs
            #artist, least popular track on album, most popular track on album, and audio features, e.g., 'min_valence, max_valence', and so on?
            
            rec = requests.get(REC_ENDPOINT,headers=headers, params=params)
            print(f'\nRecommending based on \n\n')
            for i in range(0,limit):
                for _ in range(0,len(rec.json()['tracks'][i]['artists'])):
                    print(rec.json()['tracks'][i]['artists'][_]['name'], end=" - ") #prints artist(s)
                print(f"\'{rec.json()['tracks'][i]['album']['name']}\'")
                print(rec.json()['tracks'][i]['album']['external_urls']['spotify'])
        except KeyError:
            pass
    except ValueError:
        pass

    #l = [a['artists'][b]['name'] for a in searched_albums for b in range(0,len(a['artists']))]
    #d = [a['name'] for a in searched_albums for b in range(0,len(a['artists']))]

    #TODO this maybe goes into a function that can return two track IDs from the album, the one with the lowest popularity score and the highest
    for _ in tracklist:
       t = requests.get(TRACKS_ENDPOINT+_,headers=headers)
       #print(t.json()['popularity']) #prints popularity of each track on the album
    
    #GET track audio features
    #TODO use get_audio_features() function here, but we would need to return some kind of dict that has two values, one for the least and one for the most popular track to then be inputted into the recommendatin engine
    audio = requests.get(AUDIO_FEATS_ENDPOINT+tracklist[0],headers=headers)

if __name__ == "__main__":
    main()