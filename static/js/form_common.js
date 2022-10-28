$('input').on('focusin', function() {
    $(this).parent().find('label').addClass('active');
});
  
$('input').on('focusout', function() {
    if (!this.value) {
      $(this).parent().find('label').removeClass('active');
    }
});

// 年月日のプルダウン

(function() {
    'use strict';

    var optionLoop, this_day, this_month, this_year, today;
    today = new Date();
    this_year = today.getFullYear();
    this_month = today.getMonth() + 1;
    this_day = today.getDate();

    // ループ処理
    optionLoop = function(start, end, id, this_day) {
        var i, opt;

        opt = null;
        for (i = start; i <= end; i++) {
          if (i === this_day) {
              opt += "<option value='" + i + "' selected>" + i + "</option>";
          } else {
            opt += "<option value='" + i + "'>" + i + "</option>";
          }
        }
        return document.getElementById(id).innerHTML = opt;
    };

    optionLoop(1950, this_year, 'id_year', this_year);
    optionLoop(1, 12, 'id_month', this_month);
    optionLoop(1, 31, 'id_day', this_day);
})();

$("select").on("click" , function() {
  
  $(this).parent(".select-box").toggleClass("open");
  
});

$(document).mouseup(function (e)
{
    var container = $(".select-box");

    if (container.has(e.target).length === 0)
    {
        container.removeClass("open");
    }
});


$("select").on("change" , function() {
  
  var selection = $(this).find("option:selected").text(),
      labelFor = $(this).attr("id"),
      label = $("[for='" + labelFor + "']");
    
  label.find(".label-desc").html(selection);
    
});
