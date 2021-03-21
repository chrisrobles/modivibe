$(document).ready(function() {
    $(document).on("click", "#MyPlaylists", function(e) {
        e.preventDefault();

        $.ajax({
            url: $(this).attr("href"),
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
                $(".content").first().html(response.songs);
            }
        });
    });
});