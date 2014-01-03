$(document).ready(function() {
    var entryWidth = $('.entry').width();

    $('.entry img').on('load', function() {
        if (this.naturalWidth > entryWidth || this.naturalHeight > 240) {
            $(this).addClass('expandable').on('click', function(event) {
                event.stopPropagation();
                $(this).toggleClass('expanded');
            });
        }
    });

    $('body').on('click', function() {
        $('img.expanded').removeClass('expanded');
    });
});
