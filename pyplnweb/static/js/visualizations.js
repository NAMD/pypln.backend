$(document).ready(function() {
    function visualization_text(element, data) {
        element.html('<div id="text-visualization" style="height: 400px; overflow: auto;">' +
                     data['text'].replace(/\n/g, '<br/>') + '</div>');
    }

    function visualization_token_histogram(element, data) {
        element.html('#TODO');
    }

    function visualization_pos_highlighter(element, data) {
        element.html('#TODO');
    }

    function visualization_statistics(element, data) {
        element.html('<table>\
  <tr>\
    <th>Average sentence length:</th>\
    <td>' + data['average-sentence-length'] + '</td>\
  </tr>\
  <tr>\
    <th>Repertoire:</th>\
    <td>' + data['repertoire'] + '</td>\
  </tr>\
  <tr>\
    <th>Average sentence repertoire:</th>\
    <td>' + data['average-sentence-repertoire'] + '</td>\
  </tr>\
  <tr>\
    <th>1st token distribution momentum:</th>\
    <td>' + data['momentum-1'] + '</td>\
  </tr>\
  <tr>\
    <th>2nd token distribution momentum:</th>\
    <td>' + data['momentum-2'] + '</td>\
  </tr>\
  <tr>\
    <th>3rd token distribution momentum:</th>\
    <td>' + data['momentum-3'] + '</td>\
  </tr>\
  <tr>\
    <th>4th token distribution momentum:</th>\
    <td>' + data['momentum-4'] + '</td>\
  </tr>\
  </table>');
    }

    var call_visualization = {
        'text': visualization_text,
        'token_histogram': visualization_token_histogram,
        'pos_highlighter': visualization_pos_highlighter,
        'statistics': visualization_statistics,
    };

    $('.link-visualization').click(function(event) {
        var link = $(event.target);
        var visualization = link.attr("data-visualization");
        var url = link.attr("href");
        var visualizationElement = $('#visualization');
        $.ajax(url, {success: function(data, textStatus, jqXHR) {
            $('#visualization-tabs > li > a').removeClass('active');
            visualizationElement.hide();
            call_visualization[visualization](visualizationElement, data);
            link.addClass('active');
            visualizationElement.fadeIn();
        }});
        return false;
    });

    if ($('#visualization-tabs > li > a').length > 0) {
        $($('#visualization-tabs > li > a')[0]).click();
    }
});
