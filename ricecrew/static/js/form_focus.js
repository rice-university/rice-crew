$(document).ready(function() {
    var fields = $('input[type="text"], input[type="password"]');
    for (var i = 0; i < fields.length; i++) {
        var field = fields.eq(i);
        if (!field.val()) {
            field.focus();
            return;
        }
    }
    fields.eq(0).focus();
});
