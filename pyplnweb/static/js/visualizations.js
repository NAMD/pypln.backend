$(document).ready(function() {
    function visualization_text(element, data) {
        element.html(data['text']);
    }

    function visualization_wordcloud(element, data) {
        element.html('#TODO');
    }

    function visualization_highlighter(element, data) {
        element.html('#TODO');
    }

    var call_visualization = {
        'text': visualization_text,
        'wordcloud': visualization_wordcloud,
        'pos-highlighter': visualization_highlighter,
    };

    $('.link-visualization').click(function(event) {
        var element = $(event.target);
        var visualization = element.attr("data-visualization");
        var url = element.attr("href");
        $.ajax(url, {success: function(data, textStatus, jqXHR) {
            call_visualization[visualization]($('#visualization'), data);
        }});
        return false;
    });
});
