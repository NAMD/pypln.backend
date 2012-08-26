$(document).ready(function() {
    $('.link-visualization').click(function(event) {
        var link = $(event.target);
        var visualization = link.attr("data-visualization");
        var url = link.attr("href");
        var visualizationElement = $('#visualization');
        $.ajax(url, {success: function(data, textStatus, jqXHR) {
            $('#visualization-tabs > li > a').removeClass('active');
            visualizationElement.hide();
            visualizationElement.html(data);
            link.addClass('active');
            visualizationElement.fadeIn();
        }});
        document.location.hash = visualization;
        return false;
    });

    var visualization_links = $('#visualization-tabs > li > a');
    if (visualization_links.length > 0) {
        var hash = document.location.hash;
        if (!hash) {
            $(visualization_links[0]).click();
        }
        else {
            for (var index = 0; index < visualization_links.length; index++) {
                var element = $(visualization_links[index]);
                var element_hash = '#' + element.attr('data-visualization');
                if (element_hash == hash) {
                    element.click();
                    break;
                }
            }
        }
    }
});
