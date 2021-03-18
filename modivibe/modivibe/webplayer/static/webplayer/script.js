$(document).ready(function() {
    $(document).on("click", "#MyPlaylists", function(e) {
        e.preventDefault();

        $.ajax({
            url: "my/playlists",
            type: "GET",
            success: function(response) {
                $(".content").first().html("<h1 id=\"PlaylistsList\">Playlists</h1>");

                let playlistId;
                let playlistName;

                for(const pl in response.playlists) {
                    playlistId = pl;
                    playlistName = response.playlists[pl];

                    $(".content").first().append(
                        "<div class=\"UserPlaylist\"id=\"" + playlistId + "\">\n" +
                        "<a class=\"UserPlaylistLink\" data-name=\"" + playlistName + "\" href=\"playlist/" + playlistId + "\">"
                         + playlistName +
                         "</a>" +
                        "</div>"
                    );
                }
            }
        });

    });

    $(document).on("click", ".UserPlaylistLink", function(e) {
        e.preventDefault();
        let playlistName = $(this).attr("data-name");

        $.ajax({
            url: $(this).attr("href"),
            type: "GET",
            success: function(response) {
                $(".content").first().html("<h1 class=\"PlaylistSongs\">" + playlistName + "</h1>");

                let songs = "<ul class=\"Songlist\">";
                let songNo;
                let artist;
                let songName;
                let length;

                for(const s in response.songlist) {
                    songNo = response.songlist[s]['songNo'];
                    artist = response.songlist[s]['artist'];
                    songName = response.songlist[s]['songName'];
                    length = response.songlist[s]['length'];

                    songs += "<li class=\"Song\">" + songNo + " " + songName + " by " + artist + " " + length + "</li>\n";
                }

                songs += "</ul>";

                $(".content").first().append(songs);
            }
        });
    });

});