$(document).ready(function () {
        $('#Download').click(function () {
                var selected_id = [];
                var selected_variable = [];
                var selected_starttime = [];
                var selected_endtime = [];
        {% for id in id_list %}
            {% for data in data_dict|return_item:id %}
                var checkbox = $("#"+"Check_" + {{id}} + "_" + {{data.0}});
                if(checkbox.is(':checked')){
                selected_id.push({{id}});
                selected_variable.push({{data.0}});
                selected_starttime.push({{data.1}});
                selected_endtime.push({{data.2}});
                };
            {% endfor %}
        {% endfor %}
            alert(selected_variable);
            });
});