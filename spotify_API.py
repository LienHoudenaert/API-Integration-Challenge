import base64
import urllib.parse
import requests
import json

#output formatting
from tabulate import tabulate
#tabulate uses wcwidth to handle the output of unicode strings
import wcwidth

#set variables
url = "https://accounts.spotify.com/api/token"
headers = {}
data = {}

#show some information for the user
print(" ")
print("Search for your favortie artist on Spotify via the spotify API. You will get some information about the artist, the top 10 track of the artist and the albums of the artist.")
print("To use this program you will need your client_id and your client_secret. Login at https://developer.spotify.com/dashboard/ to get your credentials!")
print("To end the python program type 'quit' or 'q' or use ctrl + c.")

try:
    while True: #keep python running until user wants to quit
    
        print(" ")
        #ask user for client_id and Client_secret
        client_id = input("client_id: ")
        if client_id == "quit" or client_id == "q":
            quit()
        client_secret = input("client_secret: ")
        if client_secret == "quit" or client_secret == "q":
            quit()

        #check is client_id AND client_secret are give, if not ask again
        if not client_secret or not client_id :
            print("You must set client_id and client_secret")   
            continue

        #encode given credentials to base64
        client_creds = f"{client_id}:{client_secret}"
        client_creds64 = base64.b64encode(client_creds.encode())

        client_creds64 = client_creds64.decode()
        #print(client_creds64)

        #set headers and data variables
        headers['Authorization'] = f"Basic {client_creds64}"
        data['grant_type'] = "client_credentials"

        #request a token 
        r = requests.post(url, headers=headers, data=data)
        
        #check if token was given and save it to variable, if not start again
        if r.status_code not in range(200, 299):
            print("Could not authenticate client! Check if credentials are correct and try again.")
            continue
        else:
            token = r.json()['access_token']
            #print(token)

        #when there is a token, keep repeating till user quits
        while token:

            #ask user for an artist name, if no name is given ask again
            print(" ")
            search = input("Name of the artist: ")
            if search == "quit" or search == "q":
                quit()
            while not search:
                print("You need to fill in a name of an artist!")
                print(" ")
                search = input("Name of the artist: ")
                if search == "quit" or search == "q":
                    quit()

            #search for the artists name on the belgian market and give back the artist that matches the most
            searchUrl = f"https://api.spotify.com/v1/search?q={search}&type=artist&limit=1&market=BE"
            #authorization with bearer and given token
            headers = {
                "Authorization": "Bearer " + token
            }

            #get results back from artist search and look for id in the json file
            json_search = requests.get(url=searchUrl, headers=headers).json()
            #if no artist if found, inform the user and ask for new name
            if json_search["artists"]["total"] == 0:
                print("No artist with the name '" + search + "' found! Try again with an other name.")
                continue
            json_id = json_search["artists"]["items"][0]["id"]

            #store id of the artist in variable 
            artistId = json_id

            #use artistId to find information about the artist with that id
            artistUrl = f"https://api.spotify.com/v1/artists/{artistId}"

            #use artistId to find the top 10 tracks of the artist with that id in Belgium
            tracksUrl = f"https://api.spotify.com/v1/artists/{artistId}/top-tracks?market=BE"

            #use artistId to find the first 50 albums of the artist with that id in Belgium
            albumsUrl = f"https://api.spotify.com/v1/artists/{artistId}/albums?limit=50&include_groups=album&market=BE"
            #use artistId to find the second 50 albums of the artist with that id in Belgium
            albumsUrl100 = f"https://api.spotify.com/v1/artists/{artistId}/albums?offset=50&limit=50&include_groups=album&market=BE"

            #use artistId to find the related artists
            relatedUrl = f"https://api.spotify.com/v1/artists/{artistId}/related-artists?limit=10"

            #get results from the info, tracks, albums and related artists search
            artist_info = requests.get(url=artistUrl, headers=headers).json()
            top_tracks = requests.get(url=tracksUrl, headers=headers).json()
            artist_albums = requests.get(url=albumsUrl, headers=headers).json()
            artist_albums100 = requests.get(url=albumsUrl100, headers=headers).json()
            related_artists = requests.get(url=relatedUrl, headers=headers).json()

            #show the found data to the user
            print("")
            print("-------------------------------------------------------------------------------")
            #basic information about the artist
            print("Name: " + artist_info["name"])
            print("Number of followers: " + str(artist_info["followers"]["total"]))
            print("Popularity: " + str(artist_info["popularity"]))
            print("Genres: " + str(artist_info["genres"]))
            print("-------------------------------------------------------------------------------")
            print("")
            #ranked top tracks of the artist
            print("Top 10 tracks of " + artist_info["name"] + ":")
            print("-------------------------------------------------------------------------------")

            #for each top tracks of artist show the results
            i = 1
            for track in top_tracks["tracks"]:
                print("  " + str(i) + ". " + track["name"])
                i = i+1

            print("-------------------------------------------------------------------------------")
            print("")

            #for each album of artist store unique album name and release date in array
            array = []
            array_name = []
            for album in artist_albums["items"]:
                album_array = [album["name"], album["release_date"]]
                album_name = album["name"]
                if album_name not in array_name:
                    array_name.append(album["name"])
                    array.append([album["name"], album["release_date"]])

            for album in artist_albums100["items"]:
                album_array = [album["name"], album["release_date"]]
                album_name = album["name"]
                if album_name not in array_name:
                    array_name.append(album["name"])
                    array.append([album["name"], album["release_date"]])
            
            #sort the array (desc) based on release date
            array.sort(key=lambda x:x[1], reverse=True)

            #show unique sorted albums with the use of the tabulate module
            print(tabulate(array, headers=["Most recent Spotify albums of " + artist_info["name"] + ":", "Release date:"]))    

            print("-------------------------------------------------------------------------------")
            print("")

            #related artists, including popularity
            #for the 8 firts related artists, store the artist name and popularity in an array
            array_related = []
            i=1
            for related in related_artists["artists"]:
                while i <= 8:
                    array_related.append([related["name"], related["popularity"]])
                    break
                i = i+1
            
            #sort the array (desc) based on popularity
            array_related.sort(key=lambda x:x[1], reverse=True)

            #show related artists with the use of the tabulate module
            print(tabulate(array_related, headers=["Related artists:", "Popularity:"]))
            print("-------------------------------------------------------------------------------")

#when program is ended due to keyboard input, quit without errors/warnings    
except KeyboardInterrupt:
    quit()
