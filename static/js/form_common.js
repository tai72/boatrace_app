$('input').on('focusin', function() {
    $(this).parent().find('label').addClass('active');
});
  
$('input').on('focusout', function() {
    if (!this.value) {
      $(this).parent().find('label').removeClass('active');
    }
});
