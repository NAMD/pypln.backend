$(document).ready(function() {
    $("#tabs").tabs();

    $('.document-link').click(function(event) {
        var element = $('#' + event.target.id);
        var destination = element.attr('href');
        $('#status-bar').html('Loading ' + element.html() + '...');
        $.ajax(destination).done(function(data) {
            $('#status-bar').html('');
            $('#document > .title').html(data.name);
            var text = '';
            var tags = '';
            for (var tokenIndex in data.tagged) {
                var info = data.tagged[tokenIndex];
                text += ' <div class="classifier classifier-' + info[1] + '">' + info[0] + '</div>';
            }
            for (var tagIndex in data.tags) {
                var tagName = data.tags[tagIndex];
                tags += ' <input type="checkbox" data-classifier="' +
            tagName + '" checked="checked">' + tagName + '</input>';
            }
            $('#document > .content').html(text);
            $('#document > #tags').html(tags);
            var tagCheckboxes = $('#tags > input');
            for (var tagIndex = 0; tagIndex < tagCheckboxes.length; tagIndex++) {
                var tagElement = $(tagCheckboxes[tagIndex]);
                tagElement.click(reloadHighlightEvent)
            reloadHighlight(tagElement);
            }
        });
        return false;
    });

    function reloadHighlightEvent(e) {
        reloadHighlight($(e.target));
    }

    function reloadHighlight(element) {
        var name = "classifier-" + element.attr('data-classifier');
        var checked = element.attr('checked');
        var showElement = checked == 'checked';
        var tokens = $('#document > .content > div');
        for (var i = 0; i < tokens.length; i++) {
            var token = $(tokens[i]);
            if (token.hasClass(name)) {
                if (showElement) {
                    token.addClass('color-' + name);
                }
                else {
                    token.removeClass('color-' + name);
                }
            }
        }
    }

});
