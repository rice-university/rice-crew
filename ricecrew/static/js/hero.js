$(document).ready(function() {
    var hero = $('div#hero'), images;

    /* We don't need to load 2x images if the window is less than 768px
       wide since the hero image is scaled down by a factor of 2 for
       smaller widths */

    if (util.retinaSupported &&
            (window.devicePixelRatio > 2 || $(window).width() >= 768)) {
        images = hero.data('images-retina');
    } else {
        images = hero.data('images');
    }

    if (!images) {
        return;
    }
    images = images.split(';');


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

    var enableControlsCallback;

    if (util.touchSupported) {
        var prevPane, currentPane, nextPane;
        var imageWidth = 2560, imageHeight = 500, transitionWidth = 32;
        var movementScale = 6.0;
        var removalTimeout;

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
            var imageScale = (hero.height() < imageHeight) ? 0.5 : 1.0;
            var delta = util.clamp(event.gesture.deltaX /
                    (transitionWidth * imageScale * movementScale),
                -1.0, 1.0);
            var prevDelta = util.clamp(delta, 0.0, 1.0),
                nextDelta = util.clamp(delta, -1.0, 0.0);

            var prevTransform = 'translate3d(' +
                ((-imageWidth + (prevDelta - 2) * transitionWidth) *
                    imageScale / 2)
                + 'px,0,0)';

            var currentTransform = 'translate3d(' +
                ((-imageWidth + (delta - 1) * transitionWidth) *
                    imageScale / 2)
                + 'px,0,0)';

            var nextTransform = 'translate3d(' +
                ((-imageWidth + nextDelta * transitionWidth) *
                    imageScale / 2)
                + 'px,0,0)';

            prevPane.css({
                '-webkit-transform': prevTransform,
                '-moz-transform': prevTransform,
                '-ms-transform': prevTransform,
                '-o-transform': prevTransform,
                'transform': prevTransform,
                'opacity': prevDelta
            });
            currentPane.css({
                '-webkit-transform': currentTransform,
                '-moz-transform': currentTransform,
                '-ms-transform': currentTransform,
                '-o-transform': currentTransform,
                'transform': currentTransform,
                'opacity': 1 - Math.abs(delta)
            });
            nextPane.css({
                '-webkit-transform': nextTransform,
                '-moz-transform': nextTransform,
                '-ms-transform': nextTransform,
                '-o-transform': nextTransform,
                'transform': nextTransform,
                'opacity': -nextDelta
            });
        };
        var handleDragEnd = function(event) {
            var imageScale = (hero.height() < imageHeight) ? 0.5 : 1.0;
            var delta = util.clamp(event.gesture.deltaX /
                    (transitionWidth * imageScale * movementScale),
                -1.0, 1.0);

            hero.removeClass('manual-transition');
            prevPane.add(currentPane).add(nextPane).css({
                '-webkit-transform': '',
                '-moz-transform': '',
                '-ms-transform': '',
                '-o-transform': '',
                'transform': '',
                'opacity': ''
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

        enableControlsCallback = function() {
            Hammer(document.getElementById('herowrapper'), {
                drag_block_horizontal: true,
                drag_block_vertical: true
            }).on('dragstart', handleDragStart)
            .on('drag', handleDrag)
            .on('dragend', handleDragEnd);
        };
    } else {
        enableControlsCallback = function() {
            prevBtn.on('click', transitionBack).show();
            nextBtn.on('click', transitionForward).show();
        };
    }


    // Set up parallax effect
    if (!util.touchSupported) {
        var navHeight = $('nav#mainnav').height();
        $(window).on('scroll', function() {
            var offset = (window.pageYOffset - navHeight) / 2;
            var transform = 'translate3d(0,' + offset + 'px,0)';
            hero.css({
                '-webkit-transform': transform,
                '-moz-transform': transform,
                '-ms-transform': transform,
                '-o-transform': transform,
                'transform': transform
            });
        });
    }


    // Download hero images sequentially
    var loadNext = function() {
        jQuery.ajax({
            url: images[loaded],
            success: function() {
                loaded += 1;
                if (loaded === 1) {
                    transitionForward();
                }
                if (loaded === 2) {
                    enableControlsCallback();
                }
            },
            error: function() {
                images.splice(loaded, 1);
            },
            complete: function() {
                if (loaded < images.length) {
                    loadNext();
                }
            }
        });
    };
    loadNext();
});
