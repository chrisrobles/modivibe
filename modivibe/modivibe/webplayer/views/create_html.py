# This file is for any python function related to creating html to insert through an ajax request


# Create a collection of items to display.
#
# param     info    List of dictionaries containing:
#                       1. contentImg: link to main content image (ex: album cover)
#                       2. contentName: content name
#                       3. contentId: id to content
#                       4. contentDesc: content description
#                   If type == albums, must also include:
#                       5. artist: artist name
#                       6. artistId: id to artist
#                       7. albumDate: album release date
#
# param     type    Type of collection, should be:
#                       album
#                       playlist
#                       artist
#                       podcast
def createCollectionItems(info, type):
    htmlStr = \
        f'''<section class="CollectionContent">
                <h1 class="ContentHeader">{type.capitalize() + 's'}</h1>
                <section class="ContentItems">
    '''
    for c in info:
        htmlStr += createItem(c, type)

    htmlStr += "\n</section>\n</section>"

    return htmlStr

# Create an album/artist/playlist/podcast item.
# This item showcases the basic information of an object and links related to it.
#
# param     info    List of dictionaries containing:
#                       1. contentImg: link to main content image (ex: album cover)
#                       2. contentName: content name
#                       3. contentId: id to content
#                       4. contentDesc: content description
#                   If type == albums, must also include:
#                       5. artist: artist name
#                       6. artistId: id to artist
#                       7. albumDate: album release date
#
# param     type    Type of collection, should be:
#                       album
#                       playlist
#                       artist
#                       podcast
def createItem(info, type):
    htmlStr = \
        f'''\n<div class="ContentItem" id="{info['contentId']}">
                    <img class="ContentImage" src="{info['contentImg']}"><br>
                    <a class="{type}Link" href="{type + '/' + info['contentId']}" data-name="{info['contentName']}">{info['contentName']}</a> '''

    if (type == 'album'):
        htmlStr += \
            f'''\n<div class="ContentArtist">
                    <a class="artistLink" id="{info['artistId']}" href="artist/{info['artistId']}">
                        {info['artist']}
                    </a>
                    <span> - {info['albumDate']}</span>
                </div>
            '''
    else:
        htmlStr += f'\n<div class="ContentDesc">{info["contentDesc"]}</div>'

    htmlStr += "</div>"

    return htmlStr

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
def createSongList(info, type):
    if not info:
        return 'Empty songlist.'

    htmlStr = \
        f'<section class="CollectionSongs">\n'

    htmlStr += \
        f'''<div class="SongHeader">
                <span class="SongNumber">#</span>
                <span class="SongName">Song</span>
                <span class="SongArtist">Artist</span>
                <span class="SongLength">Length</span>
            </div>
    '''

    htmlStr += \
        f'''<section class="SongList">
                <div class="SongItems">
    '''

    for song in info:
        htmlStr += \
            f'''    <div class="Song">
                        <span class="SongNumber">{song['songNum']}</span>
                        <span class="SongName"><a href="placeholder/{song['songId']}">{song['songName']}</a></span>
                        <span class="SongArtist"><a href="artist/{song['artistId']}">{song['songArtist']}</a></span>
                        <span class="SongLength">{convertToMinSec(song['songLength'])}</span>
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
    ms = length % 1000
    length //= 1000
    min = length // 60
    sec = length % 60

    if sec > 60:
        min += 1
        sec %= 60

    min = str(min)
    sec = str(sec)

    if int(sec) < 10:
        sec = '0' + sec

    return (min + ':' + sec)