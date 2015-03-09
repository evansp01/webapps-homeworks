$( "#post_list" ).on( "submit", "form", function( event ) {
  event.preventDefault();
  console.log($(this).serialize());
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
    error: function (xhr, ajaxOptions, thrownError) {
      console.log(xhr.status);
      console.log(thrownError);
    }
  });
});