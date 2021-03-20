$(document).ready(function() {
    $(document).on("click", "#MyPlaylists", function(e) {
        e.preventDefault();

        $.ajax({
            url: "my/playlists",
            type: "GET",
            success: function(response) {
                  $(".content").first().html(response.playlists);
            }
        });

    });

    $(document).on("click", ".playlistLink", function(e) {
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