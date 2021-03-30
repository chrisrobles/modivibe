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
                $(".content").first().html(response.songs);
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
