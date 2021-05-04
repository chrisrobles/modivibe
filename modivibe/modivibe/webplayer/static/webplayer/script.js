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
                if(response.status == 200) {
                  $(".content").first().html(response.collection);
                  $("html, .content").animate({ scrollTop: 0 }, "fast");

                }
                else {
                    window.location="/"; // redirect
                }
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
                if(response.status == 200) {
                    $(".content").first().html(response.page);
                    $("html, .content").animate({ scrollTop: 0 }, "fast");

                }
                else {
                    window.location="/";
                }
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
                if(response.status == 200) {
                    $(".ArtistItemButton").removeAttr("style");
                    $(".ArtistItemButton"+dataType).attr("style", "background-color: rgba(255, 255, 255, 0.25);");
                    $(".ArtistItemsContent").first().html(response.content);
                    $(".CollectionContent .row .col-12 .ContentHeader").remove();
                    $(".CollectionContent .row:first").attr("style", "margin: 15px 0px 15px 0px"); // for spacing between tabs and content
                    $("html, .content").animate({ scrollTop: 0 }, "fast");
                }
                else {
                    window.location="/";
                }
            }
        });
    });

    $(document).on("click", ".setColor", function(e) {
        var color = $('.colorSchemeInput').val();
        $('.colorScheme').css('background-color', $('.colorSchemeInput').val());
        color = color.match(/[A-Za-z0-9]{2}/g);
        color = color.map(function(v) { return parseInt(v, 16) });
        console.log(color);
        color[0] -= 40;
        color[1] -= 40;
        color[2] -= 40;
        
        $('.sidebar').css('background-color', "rgb(" + color.join(",") + ")");
        color[0] += 60;
        color[1] += 60;
        color[2] += 60;
        $('.content').css('background-color', "rgb(" + color.join(",") + ")")
    });

    $(document).on("keydown", "#searchInput", function(e) {
        if(e.keyCode == 13) {
            e.preventDefault();
            let input = $(this).val();
            $(this).attr("value", input);

            // if input
            if(input) {
                $.ajax({
                    url: "/search/"+input,
                    type: "GET",
                    success: function(response) {
                        if(response.status == 200) {
                            console.log("Search success.");
                            $(".content").first().html(response.searchResults);
                            $("button.PlayRequest").remove();
                            $("html, .content").animate({ scrollTop: 0 }, "fast");
                        }
                        else {
                            window.location="/";
                        }
                    }
                });
            }
            else {
                console.log("Empty search value.");
            }
        }
    });
});
