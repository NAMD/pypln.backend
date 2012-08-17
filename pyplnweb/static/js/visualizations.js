$(document).ready(function() {
    function roundString(number, digits) {
        var tens = Math.pow(10, digits);
        var newNumber = Math.round(number * tens) / tens;
        var parts = String(newNumber).split(".");
        var digitsLeft;
        if (parts.length == 1) {
            digitsLeft = digits;
            newNumber = parts[0] + ".";
        }
        else {
            digitsLeft = digits - parts[1].length;
            newNumber = String(newNumber);
        }
        for (var i = 0; i < digitsLeft; i++) {
            newNumber += "0";
        }
        return newNumber;
    }

    function visualization_text(element, data) {
        element.html('<div id="text-visualization" style="height: 400px; overflow: auto;">' +
                     data['text'].replace(/\n/g, '<br/>') + '</div>');
    }

    function visualization_token_histogram(element, data) {
        element.html('<center><div style="width: 480px; height: 400px" id="plot"></div>\
  Statistical data:\
  <table>\
  <tr>\
    <th>Mean (token distribution):</th>\
    <td class="right">' + roundString(data['momentum-1'], 2) + '</td>\
  </tr>\
  <tr>\
    <th>Variance (token distribution):</th>\
    <td class="right">' + roundString(data['momentum-2'], 2) + '</td>\
  </tr>\
  <tr>\
    <th>Skewness (token distribution):</th>\
    <td class="right">' + roundString(data['momentum-3'], 2) + '</td>\
  </tr>\
  <tr>\
    <th>Kurtosis (token distribution):</th>\
    <td class="right">' + roundString(data['momentum-4'], 2) + '</td>\
  </tr>\
  </table></center>');
        var aggregate = {};
        var freqdist = data['freqdist'];
        for (var index = 0; index < freqdist.length; index++) {
            var value = freqdist[index][1];
            if (aggregate[value] == undefined) {
                aggregate[value] = 1;
            }
            else {
                aggregate[value] = aggregate[value] + 1;
            }
        }
        var points = [];
        for (key in aggregate) {
            points.push([key, aggregate[key]]);
        }
        $.plot($('#plot'), [ { data: points, bars: { show: true } } ]);
    }

    function visualization_pos_highlighter(element, data) {
        element.html('#TODO');
    }

    function visualization_statistics(element, data) {

        element.html('<table>\
  <tr>\
    <th>Number of tokens:</th>\
    <td class="right">' + data['tokens'].length + '</td>\
  </tr>\
  <tr>\
    <th>Number of sentences:</th>\
    <td class="right">' + data['sentences'].length + '</td>\
  </tr>\
  <tr>\
    <th>Average sentence length (in tokens):</th>\
    <td class="right">' + roundString(data['average-sentence-length'], 2) + '</td>\
  </tr>\
  <tr>\
    <th>Repertoire:</th>\
    <td class="right">' + roundString(data['repertoire'] * 100, 2) + '%</td>\
  </tr>\
  <tr>\
    <th>Average sentence repertoire:</th>\
    <td class="right">' + roundString(data['average-sentence-repertoire'] * 100, 2) + '%</td>\
  </tr>\
  </table>');
    }

    var call_visualization = {
        'text': visualization_text,
        'token-frequency-histogram': visualization_token_histogram,
        'pos-highlighter': visualization_pos_highlighter,
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
