var array = {{
               {% for x in disabled_dates %}
               {{x.dates}}
               {% endfor  %}
            }}

$('datepicker').datepicker({
    beforeShowDay: function(date){
        var string = jQuery.datepicker.formatDate('yy-mm-dd', date);
        return array.indexOf(string) != -1 ? [false] : $.datepicker.noWeekends(date);
    }
});