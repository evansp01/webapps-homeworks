$( "#post_list" ).on( "submit", "form", function( event ) {
  event.preventDefault();
  thisForm = $(this);
  $.ajax({
    url: $(this).attr("action"),
    type: 'post',
    dataType: 'html',
    data: $(this).serialize(),
    success: function(data) {
      myNode = thisForm.siblings("ul.list-unstyled");
      thisForm.children("input.form-control").val("");
      thisForm.children("button").blur();
      myNode.html(data);

    },
  });
});
