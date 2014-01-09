$(document).ready(function() {
    var hero = $('div#hero');
    var images = hero.data('images');
    var touchSupported = 'ontouchend' in document;

    if (!images) {
        return;
    }


    // Set up hero transitions
    var prevBtn = $('a#heroprev'), nextBtn = $('a#heronext');
    var loaded = 0;
    var current = -1;
    var transitionInterval = 10000;
    var transitionTimeout, domTimeout1, domTimeout2;
    var transitionPending = false;

    var transitionForward = function() {
        clearTimeout(transitionTimeout);
        transitionTimeout = setTimeout(transitionForward, transitionInterval);

        current = (current + 1) % loaded;
        var currentPane = hero.children().not('.prev, .next');
        var nextPane = $('<img class="next" />')
            .attr('src', images[current]).appendTo(hero);

        transitionPending = true;
        domTimeout1 = setTimeout(function() {
            currentPane.addClass('prev');
            nextPane.removeClass('next');
            transitionPending = false;
        }, 50);
        domTimeout2 = setTimeout(function() {
            currentPane.remove();
        }, 1000);
    };
    var transitionBack = function() {
        clearTimeout(transitionTimeout);
        transitionTimeout = setTimeout(transitionForward, transitionInterval);

        current = (current + loaded - 1) % loaded;
        var currentPane = hero.children().not('.prev, .next');
        var prevPane = $('<img class="prev" />')
            .attr('src', images[current]).appendTo(hero);

        transitionPending = true;
        domTimeout1 = setTimeout(function() {
            currentPane.addClass('next');
            prevPane.removeClass('prev');
            transitionPending = false;
        }, 50);
        domTimeout2 = setTimeout(function() {
            currentPane.remove();
        }, 1000);
    };

    var enableUserControl;

    if (touchSupported) {
        var prevPane, currentPane, nextPane;
        var imageWidth = 2000, imageHeight = 492, transitionWidth = 48;
        var movementScale = 6.0;
        var removalTimeout;
        var clamp = function(x, min, max) {
            return x < min ? min : (x > max ? max : x);
        };

        var handleDragStart = function(event) {
            clearTimeout(transitionTimeout);
            clearTimeout(removalTimeout);
            if (transitionPending) {
                clearTimeout(domTimeout1);
                clearTimeout(domTimeout2);
            }
            var prev = (current + loaded - 1) % loaded,
                next = (current + 1) % loaded;

            hero.addClass('manual-transition');
            currentPane = hero.children().not('.prev, .next');

            prevPane = prevPane || $('<img class="prev" />')
                .attr('src', images[prev]).appendTo(hero);
            nextPane = nextPane || $('<img class="next" />')
                .attr('src', images[next]).appendTo(hero);
        };
        var handleDrag = function(event) {
            var imageScale = hero.height() < imageHeight ? 0.5 : 1.0;
            var delta = clamp(event.gesture.deltaX /
                    (transitionWidth * imageScale * movementScale),
                -1.0, 1.0);
            var prevDelta = clamp(delta, 0.0, 1.0),
                nextDelta = clamp(delta, -1.0, 0.0);

            prevPane.css({
                left: ((-imageWidth + (prevDelta - 2) * transitionWidth) *
                    imageScale / 2) + 'px',
                opacity: prevDelta
            });
            currentPane.css({
                left: ((-imageWidth + (delta - 1) * transitionWidth) *
                    imageScale / 2) + 'px',
                opacity: 1 - Math.abs(delta)
            });
            nextPane.css({
                left: ((-imageWidth + nextDelta * transitionWidth) *
                    imageScale / 2) + 'px',
                opacity: -nextDelta
            });
        };
        var handleDragEnd = function(event) {
            var imageScale = hero.height() < imageHeight ? 0.5 : 1.0;
            var delta = clamp(event.gesture.deltaX /
                    (transitionWidth * imageScale * movementScale),
                -1.0, 1.0);

            hero.removeClass('manual-transition');
            prevPane.add(currentPane).add(nextPane).css({
                left: '',
                opacity: ''
            });

            if (delta > 0.6) {
                current = (current + loaded - 1) % loaded;
                prevPane.removeClass('prev');
                prevPane = null;
                nextPane.remove();
                nextPane = currentPane.addClass('next');
            } else if (delta < -0.6) {
                current = (current + 1) % loaded;
                nextPane.removeClass('next');
                nextPane = null;
                prevPane.remove();
                prevPane = currentPane.addClass('prev');
            }

            removalTimeout = setTimeout(function() {
                $().add(prevPane).add(nextPane).remove();
                prevPane = nextPane = null;
            }, 1000);
            transitionTimeout = setTimeout(transitionForward,
                                           transitionInterval);
        };

        enableUserControl = function() {
            Hammer(document.getElementById('herowrapper'), {
                drag_block_horizontal: true,
                drag_block_vertical: true
            }).on('dragstart', handleDragStart)
            .on('drag', handleDrag)
            .on('dragend', handleDragEnd);
        };
    } else {
        enableUserControl = function() {
            prevBtn.on('click', function(event) {
                event.preventDefault();
                transitionBack();
            }).show();
            nextBtn.on('click', function(event) {
                event.preventDefault();
                transitionForward();
            }).show();
        };
    }


    // Set up parallax effect
    if (!touchSupported) {
        var navHeight = $('nav#mainnav').height();
        $(window).on('scroll', function() {
            var offset = (window.pageYOffset - navHeight) / 2;
            hero.css('top', offset + 'px');
        });
    } else {
        hero.css('top', '0');
    }


    // Download hero images sequentially
    images = images.split(';');
    var getNext = function() {
        jQuery.ajax({
            url: images[loaded],
            success: function() {
                loaded += 1;
                if (loaded < images.length) {
                    getNext();
                }
                if (loaded === 1) {
                    transitionForward();
                }
                if (loaded === 2) {
                    enableUserControl();
                }
            },
            error: function() {
                images.splice(loaded, 1);
                if (loaded < images.length) {
                    getNext();
                }
            }
        });
    };
    getNext();
});
