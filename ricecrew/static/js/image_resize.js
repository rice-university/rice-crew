$(document).ready(function() {
    var entryWidth = $('.entry').width();

    var handleImage = function() {
        if (this.naturalWidth > entryWidth || this.naturalHeight > 240) {
            $(this).addClass('expandable').off('click').on('click',
                function(event) {
                    event.stopPropagation();
                    $(this).toggleClass('expanded');
                });
        }
    };

    $('.entry img').each(handleImage).on('load', handleImage);
    $('body').on('click', function() {
        $('img.expanded').removeClass('expanded');
    });
});
