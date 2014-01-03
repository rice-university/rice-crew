$(document).ready(function() {
    var hero = $('div#hero');


    // Set up hero image transitions
    var images = hero.data('images');
    var prevBtn = $('a#heroprev'), nextBtn = $('a#heronext');
    var loaded = 0;
    var current = -1;

    var transitionForward = function() {
        if (loaded > 1 || (loaded === 1 && current === -1)) {
            current = (current + 1) % loaded;
            var image = images[current];
            var currentPane = hero.children().not('.prev, .next');
            var nextPane = $('<img class="next" />').attr('src', image)
                .appendTo(hero);

            setTimeout(function() {
                currentPane.addClass('prev');
                nextPane.removeClass('next');
            }, 0);
            setTimeout(function() {
                currentPane.remove();
            }, 1000);
        }
    };

    var transitionBack = function() {
        if (loaded > 1 || (loaded === 1 && current === -1)) {
            current = (current + loaded - 1) % loaded;
            var image = images[current];
            var currentPane = hero.children().not('.prev, .next');
            var prevPane = $('<img class="prev" />').attr('src', image)
                .appendTo(hero);

            setTimeout(function() {
                currentPane.addClass('next');
                prevPane.removeClass('prev');
            }, 0);
            setTimeout(function() {
                currentPane.remove();
            }, 1000);
        }
    };

    if (images) {
        // Download the images sequentially
        images = images.split(';');
        var getNext = function() {
            jQuery.ajax({
                'url': images[loaded],
                'success': function() {
                    loaded += 1;
                    if (loaded < images.length) {
                        getNext();
                    }
                    if (loaded === 1) {
                        transitionForward();
                    }
                    if (loaded === 2) {
                        prevBtn.add(nextBtn).show();
                    }
                }
            });
        };
        getNext();

        // Transition every 10s and with back/forward buttons
        var transitionInterval = setInterval(transitionForward, 10000);
        prevBtn.on('click', function() {
            transitionBack();
            clearInterval(transitionInterval);
            transitionInterval = setInterval(transitionForward, 10000);
        });
        nextBtn.on('click', function() {
            transitionForward();
            clearInterval(transitionInterval);
            transitionInterval = setInterval(transitionForward, 10000);
        });
    }


    // Set up parallax effect
    var navHeight = $('nav#mainnav').height();
    $(window).on('scroll', function() {
        var offset = (window.pageYOffset - navHeight) / 2;
        hero.css('top', offset + 'px');
    });

});
