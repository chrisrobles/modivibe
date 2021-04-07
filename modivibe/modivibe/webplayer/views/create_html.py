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
def createCollectionItems(info, type): # DEPRECATED
    htmlStr = \
        f'''<div class="container-fluid">
                <section class="CollectionContent">
                    <div class="row">
                        <div class="col-12">
                            <h1 class="ContentHeader">{type.capitalize() + 's'}</h1>
                        </div>
                    </div>
                    <section class="ContentItems">
                        <div class="row">
    '''
    count = 0
    for c in info:
        htmlStr += createItem(c, type)
        count += 1
        if(count == 3):
            count = 0
            htmlStr += "</div><div class='row'>"
    
    htmlStr += "</div>"

    htmlStr += "\n</section>\n</section></div>"

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
def createItem(info, type): # DEPRECATED
    htmlStr = ""
    if (type == 'album'):
        htmlStr += \
        f'''\n
        <div style="padding-bottom: 20px;" class="col-4">
        <div class="ContentItem" id="{info['contentId']}">
            <img class="ContentImage" src="{info['contentImg']}"><br>
            <a class="{type}Link" href="{type + '/' + info['contentId']}" data-name="{info['contentName']}">{info['contentName']}</a> '''
        htmlStr += \
            f'''\n
            <div class="ContentArtist">
                    <a class="artistLink" id="{info['artistId']}" href="artist/{info['artistId']}">
                        {info['artist']}
                    </a>
                    <span> - {info['albumDate']}</span>
                </div>
            </div>
            '''
    elif (type == 'playlist'):
        htmlStr += \
        f'''\n
        <div style="padding-bottom: 20px;" class="col-4">
            <div class="ContentItem" id="{info['contentId']}">
            <img class="ContentImage" src="{info['contentImg']}"><br>
            <a class="{type}Link" style="text-align:center;" href="{type + '/' + info['contentId']}" data-name="{info['contentName']}"><h3>{info['contentName']}</h3></a> '''
        #htmlStr += f'\n<div class="ContentDesc">{info["contentDesc"]}</div></div>'
        htmlStr += "</div>"
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
def createSongList(info, type, context_uri):
    if not info:
        return 'Empty songlist.'

    htmlStr = \
        f'''
        <button class="PlayRequest" data-uri="{context_uri}">PLAY {type.upper()}</button>
        <section class="CollectionSongs">\n'''

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
            f'''    <div class="Song" data-uri="{song['songURI']} data-parent-uri='{context_uri}">
                        <span class="SongNumber PlayRequest" data-number="{song['songNum']}" data-uri="{song['songURI']}" data-parent-uri="{context_uri}">{song['songNum']}</span>
                        <span class="SongName"><a href="placeholder/{song['songId']}">{song['songName']}</a></span>
                        <span class="SongArtist Artist"><a href="artist/{song['artistId']}" data-uri="{song['artistId']}">{song['songArtist']}</a></span>
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