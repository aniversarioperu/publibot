$.getJSON("cherry_tweets.json", function(data) {
    var items = [];
    $.each(data, function(key, val){
        var out = "<div class='media'>\n";
        out += "<span class='pull-left' href='#'>";
        out += "<img class='img-rounded' src='avatars/" + val.screen_name + ".jpg' />";
        out += "</span>\n";

        out += "<span class='pull-right' href='#'><a href='https://twitter.com/" + val.screen_name + "/status/" + val.tweet_id + "'>";
        out += val.created_at;
        out += "</a></span>\n";

        out += "<div class='media-body'>";
        out += "<b><a href='https://twitter.com/" + val.screen_name + "'>@" + val.screen_name.toUpperCase() + "</a></b><br />\n";
        out += val.status;
        out += "</div>\n";

        out += "<div class='media-footer'>";
        out += "<ul class='pull-left'>\n";
        out += "<li><a href='screenshots/" + val.tweet_id + ".png'>Cached Copy</a></li>";
        out += "</ul>\n";

        out += "<ul class='pull-right'>\n";
        out += "<li><a role='button' class='icon-reply' href='https://twitter.com/intent/tweet?in_reply_to=" + val.tweet_id + "'><span>&nbsp;&nbsp;&nbsp;&nbsp;Reply&nbsp;</span></a></li>";
        out += "<li><a role='button' class='icon-retweet' href='https://twitter.com/intent/retweet?tweet_id=" + val.tweet_id + "'><span>&nbsp;&nbsp;&nbsp;&nbsp;Retweet&nbsp;</span></a></li>";
        out += "<li><a role='button' class='icon-favorite' href='https://twitter.com/intent/favorite?tweet_id=" + val.tweet_id + "'><span>&nbsp;&nbsp;&nbsp;&nbsp;Favorite&nbsp;</span></a></li>";
        out += "</ul>";
        out += "</div>\n\n";
        items.push(out);
    });

    $("#tuits").append(items);
});
