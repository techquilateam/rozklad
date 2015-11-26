var $ = django.jQuery

function check_identifier() {
    var identifier_str = $("#id_identifier").val()
    
    if (identifier_str.indexOf("/") != -1) {
        identifier_str = identifier_str.split("/")
        identifier_str = identifier_str[identifier_str.length - 1]
    }

    $.ajax({
        method: "GET",
        url: "https://api.vk.com/method/users.get",
        dataType: "jsonp",
        data: {
            user_ids: identifier_str,
            v: "5.40"
        }
    }).success(function(data) {
        if ((typeof data.response != "undefined") && (data.response.length > 0)) {
            identifier_str = "VK ID is: " + data.response[0].id
        } else {
            identifier_str = "No VK ID"
        }

        $("#id_identifier_help").text(identifier_str)
    })
}

$(document).ready(function($) {
    $(".field-identifier div").append($("<p>", {
        class: "help",
        id: "id_identifier_help",
    }))

    check_identifier()

    $("#id_identifier").keyup(function() {
        check_identifier()
    })

    SelectFilter.init("id_groups", "groups", 0, "/static/admin/");
    SelectFilter.init("id_teachers", "teachers", 0, "/static/admin/");
})
