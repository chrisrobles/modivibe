$(document).ready(function() {
    // comment this out, and uncomment the ones in each function when testing back/forward button
    window.history.replaceState({}, "", "/webplayer");
    $(document).on("click", ".SideBarUserCollection", function(e) {
        e.preventDefault();
        //window.history.pushState({}, "", $(this).attr("href"));

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
       // window.history.pushState({}, "", $(this).attr("href"));

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
        //window.history.pushState({}, "", $(this).attr("href"));
        let dataType = "[data-tab=" + $(this).children(".ArtistItemButton:first").data("tab") + "]";

        $.ajax({
            url: $(this).attr("href"),
            type: "GET",
            data: {
                'fromArtistPage': true
            },
            success: function(response) {
                $(".ArtistItemButton").removeAttr("style");
                $(".ArtistItemButton"+dataType).attr("style", "background-color: rgba(255, 255, 255, 0.25);");
                $(".ArtistItemsContent").first().html(response.content);
                $(".CollectionContent .row .col-12 .ContentHeader").remove();
                $(".CollectionContent .row:first").attr("style", "margin: 15px 0px 15px 0px"); // for spacing between tabs and content
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
