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
        document.location.hash = visualization.replace(/_/g, '-');
        return false;
    });

    if ($('#visualization-tabs > li > a').length > 0) {
        var hash = document.location.hash;
        var visualization_tabs = $('#visualization-tabs > li > a');
        for (var index = 0; index < visualization_tabs.length; index++) {
            var element = $(visualization_tabs[index]);
            var element_hash = '#' + element.attr('data-visualization').replace(/_/g, '-');
            if (element_hash == hash) {
                element.click();
                break;
            }
        }
    }
});
