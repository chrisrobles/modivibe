$(document).ready(function() {
    window.history.replaceState({}, "", "/webplayer");
    $(document).on("click", ".SideBarUserCollection", function(e) {
        e.preventDefault();

        $.ajax({
            url: $(this).attr("href"),
            type: "GET",
            success: function(response) {
                  $(".content").first().html(response.collection);
            }
        });

    });

    $(document).on("click", ".ItemLink", function(e) {
        e.preventDefault();

        $.ajax({
            url: $(this).attr("href"),
            type: "GET",
            success: function(response) {
                $(".content").first().html(response.page);
            }
        });
    });

    $(document).on("click", ".ArtistItems", function(e) {
        e.preventDefault();
        console.log("artist item request");

        $.ajax({
            url: $(this).attr("href"),
            type: "GET",
            data: {
                'fromArtistPage': true
            },
            success: function(response) {
                $(".ArtistItemsContent").first().html(response.content);
                console.log("artist item inserted");
            }
        });
    });

//    $(document).on("click","#myAlbums",function(e) {
//        e.preventDefault();
//
//        $.ajax({
//            url: $(this).attr("href"),
//            type: "Get",
//            success: function (response) {
//                $(".content").first().html(response.myAlbums);
//            }
//        });
//    });
});
