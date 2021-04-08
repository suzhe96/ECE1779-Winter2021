function read_more ( comment_id, btn_id){
  bt = document.getElementById(btn_id);
  comment = document.getElementById(comment_id);
    var elem = $(bt).text();
    if (elem == "Read More") {
      //Stuff to do when btn is in the read more state
      $(bt).text("Read Less");
      $(comment).slideDown();
    } else {
      //Stuff to do when btn is in the read less state
      $(bt).text("Read More");
      $(comment).slideUp();
    }
};