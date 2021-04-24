# This file is for any python function related to creating html to insert through an ajax request
# will probably turn into a helper file

# Create a list of songs based on the list of info given.
#
#   param   info    List of dictionaries with:
#                       1. songNum:     Song number based on item it's a list of
#                       2. songName:    Name of song
#                       3. songId:      Song id
#                       4. songArtist:  Name of main artist
#                       5. artistId:    Artist id
#                       6. songLength:  Duration of song in milliseconds
#
#   param     type    Type of collection, should be:
#                       album
#                       playlist
#                       artist (for an artists top songs)
#
# NOTE: Podcast is not part of this. How an episode displays information is different than a song.
def createSongList(info, type, context_uri):
    if not info:
        return 'Empty songlist.'

    htmlStr = \
        f'''
        <button class="PlayRequest" data-uri="{context_uri}">PLAY {type.upper()}</button>
        <section class="CollectionSongs">\n'''

    htmlStr += \
        f'''<div class="SongHeader row">
                <div class ="col-1">
                    <span class="SongNumber"><h3 style="color: white;">#</h3></span>
                </div>
                <div class="col-5">
                    <span class="SongName"><h3 style="color: white;">Song</h3></span>
                </div>
                <div class="col-5">
                    <span class="SongArtist"><h3 style="color: white;">Artist</h3></span>
                </div>
                <div class="col-1">
                    <span class="SongLength"><h3 style="color: white;">Length</h3></span>
                </div>
            </div>
    '''

    htmlStr += \
        f'''<section class="SongList">
                <div class="SongItems">
    '''

    for song in info:
        htmlStr += \
            f'''    <div class="Song row" data-uri="{song['songURI']} data-parent-uri='{context_uri}">
                        <div class="col-1">
                            <span class="SongNumber PlayRequest" data-number="{song['songNum']}" data-uri="{song['songURI']}" data-parent-uri="{context_uri}">{song['songNum']}</span>
                        </div>
                        <div class="col-5">
                            <span class="SongName">{song['songName']}</span>
                        </div>
                        <div class="col-5">
                            <span class="SongArtist Artist"><a class='ItemLink' href="artist/{song['artistId']}" data-uri="spotify:artist:{song['artistId']}">{song['songArtist']}</a></span>
                        </div>
                        <div class="col-1">
                            <span class="SongLength">{convertToMinSec(song['songLength'])}</span>
                        </div>
                    </div>
    '''

    htmlStr += \
        f'''    </div>
            </section>
        </section>         
    '''

    return htmlStr

# Convert integer length of a song in milliseconds to string of minutes and seconds
def convertToMinSec(length):
    length //= 1000
    min = length // 60
    sec = length % 60

    min = str(min)
    sec = str(sec)

    if int(sec) < 10:
        sec = '0' + sec

    return (min + ':' + sec)

# gets information needed to create a header for an artist
def getArtistHeaderInfo(sp, artist_id):
    ar = sp.artist(artist_id)
    isUserFollowing = sp.current_user_following_artists(ids=[ar['uri']])[0]
    return {
        'artistName': ar['name'],
        'artistImg': ar['images'][0]['url'] if ar['images'] else 'default',
        'artistFollowers': ar['followers']['total'],
        'artistId': ar['id'],
        'artistGenres': ar['genres'][:7],
        'followingArtist': isUserFollowing
    }

