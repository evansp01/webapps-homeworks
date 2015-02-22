last_feed_data = -1
window.setInterval(function () {
  $.ajax({
      url: "/feed/home",
      dataType : "json",
      data : {"last" : last_feed_data},
      success: function( items ) {
        $("#post_list").prepend(items.html)
        last_feed_data = items.last;
          // Removes the old to-do list items
      }
  });
}, 5000);
