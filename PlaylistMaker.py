import glob
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pyfiglet import figlet_format   #fonts http://www.figlet.org/examples.html
from progress.bar import IncrementalBar

def createPlaylist(user, name, public, collaborative, description):
    try:
        sp.user_playlist_create(user, name, public=public, collaborative=collaborative, description=description)
        print("Playlist created")
    except Exception as e:
        print(e)


def checkMp3Files(path):
    counter = len(glob.glob1(path, "*.mp3"))
    if counter == 0:
        print("There are no mp3 files in this directory")
        return False

    if counter > 100:
        print("There can only be a max of 100 mp3 files in the directory")
        return False

    print("There are " + str(counter) + " mp3 files in the directory")
    return True

def getSongList(path):
    songs = [os.path.splitext(os.path.basename(x))[0] for x in
             glob.glob(path + '\*.mp3')]
    return songs

def getUrisList(songs):
    bar = IncrementalBar('Getting songs uris', max=len(songs))
    track_uris = []
    for q in songs:
        result = sp.search(q, type='track')
        items = result['tracks']['items']
        if len(items) > 0:
            track_uris.append(items[0]['uri'])
            bar.next()
    bar.finish()
    return track_uris

def bye():
    print("\n=================================")
    print("            Bye bye              ")
    print("=================================\n")
    exit()

def main():
    #Menú
    print("##############################################################################")
    print(figlet_format("Playlist Maker", font="doom"))
    print("##############################################################################\n")

    print("What do you want to do?: \n")
    print("[1] - Create playlist")
    print("[2] - Add songs to playlist")

    while True:
        option = input("\nEnter option: ")

        if option == "exit":
            bye()

        if option in ('1', '2'):
            break
        print("Invalid input.")

    #Create playlist
    if option == "1":
        user = sp.me()['id']
        name = input("\nEnter the name of the playlist you want to create: ")

        while True:
            public = input("\nDo you want the playlist to be public? (y/n): ")
            if public in ('y', 'n'):
                break
            print("Invalid input.")

        if public == 'y':
            public = True
            collaborative = False #Public playlists can't be collaborative
        else:
            public = False

            while True:
                collaborative = input("\nIs the playlist collaborative? (y/n): ")
                if collaborative in ('y', 'n'):
                    break
                print("Invalid input.")

            if collaborative == 'y':
                collaborative = True
            else:
                collaborative = False

        description = input("\nAdd a description to your playlist: ")

        createPlaylist(user, name, public, collaborative, description)

    #Add songs to playlist
    if option == "2":
        results = sp.user_playlists(sp.me()['id'])

        if len(results['items']) > 0:
            print("\nTo which playlist do you want to add the tracks?")
            for i in range(len(results['items'])):
               print(str([i]) + " - " + results['items'][i]['name'])

            #Select playlist
            while True:
                try:
                    choice = int(input("\nChoice: "))
                    if choice == -99:
                        bye()
                    if choice in range(len(results['items'])):
                        playlist = results['items'][choice]['name']
                        playlist_id = results['items'][choice]['id']
                        print("You are going to add the tracks to the following playlist: " + playlist)
                        break
                    print("Invalid input.")
                except ValueError:
                    print("You can only enter numbers. Type -99 to exit program")
                    continue

            #Enter path
            while True:
                folder_path = input("\nEnter the path of the folder that contains the tracks: (Press enter if you want to use de current script directory)")

                if folder_path == "exit":
                    bye()

                if folder_path == "": #if path is empty get the default file's path
                    folder_path = os.getcwd()
                    if not checkMp3Files(folder_path): #if the path doesnt have any mp3 files it asks again for a directory
                        continue
                    break

                if os.path.isdir(folder_path):
                    if not checkMp3Files(folder_path):
                        continue
                    break
                print("Can't find the path: " + folder_path + ". Type 'exit' to exit the program")

            #Get the songs
            songs = getSongList(folder_path)
            track_uris = getUrisList(songs)

            print("\nAdding the tracks to the playlist. It might take a while...")
            try:
                sp.playlist_add_items(playlist_id,track_uris, position=None)
            except Exception as e:
                print("Error: " + e)


            print("\n Tracks added to the playlist")
            print("-------------------------------")


if __name__ == '__main__':
    # Auth on spotify
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="Client ID",  # YourApp Client ID
                                                   client_secret="Client_Secret",  # Your Client_Secret
                                                   redirect_uri="http://localhost:8888/callback/",
                                                   scope="user-library-read playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative "))

    main()
