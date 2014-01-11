$(document).ready(function() {
    var images = $('.entry img');

    if (util.touchSupported) {
        images.each(function() {
            var self = $(this);
            var scale = 1.0, initScale = scale, maxScale;
            var translateX = 0, translateY = 0,
                initX = translateX, initY = translateY;

            var applyTransform = function() {
                var transformValue = 'translate(' + translateX + 'px, ' +
                    translateY + 'px) scale(' + scale + ')';
                self.css({
                    '-webkit-transform': transformValue,
                    '-moz-transform': transformValue,
                    '-ms-transform': transformValue,
                    '-o-transform': transformValue,
                    'transform': transformValue
                });
            };

            var handleTouch = function() {
                self.addClass('manual-transition');
                maxScale = Math.min(this.naturalWidth / self.width(),
                                    this.naturalHeight / self.height());
            };
            var handleRelease = function() {
                self.removeClass('manual-transition');
                scale = initScale = util.clamp(scale, 1.0, maxScale);
                var xMin = (1 - scale) * self.width() / 2;
                var xMax = (scale - 1) * self.width() / 2;
                var yMin = (1 - scale) * self.height() / 2;
                var yMax = (scale - 1) * self.height() / 2;
                translateX = initX = util.clamp(translateX, xMin, xMax);
                translateY = initY = util.clamp(translateY, yMin, yMax);
                applyTransform();
            };

            var handleDoubleTap = function() {
                scale = (scale < maxScale) ? maxScale : 1.0;
            };
            var handleTransform = function(event) {
                scale = initScale * event.gesture.scale;
                applyTransform();
            };
            var handleTransformEnd = function() {
                initScale = scale;
            }
            var handleDrag = function(event) {
                translateX = initX + event.gesture.deltaX;
                translateY = initY + event.gesture.deltaY;
                applyTransform();
            };
            var handleDragEnd = function() {
                initX = translateX;
                initY = translateY;
            };

            Hammer(this, {
                drag_block_horizontal: true,
                drag_block_vertical: true,
                transform_always_block: true
            }).on('touch', handleTouch)
            .on('release', handleRelease)
            .on('doubletap', handleDoubleTap)
            .on('transform', handleTransform)
            .on('transformend', handleTransformEnd)
            .on('drag', handleDrag)
            .on('dragend', handleDragEnd)
            ;
        });

    } else {
        var entryWidth = $('.entry').width();
        var tempElement = $('<p>test</p>').appendTo('body');
        var emSize = tempElement.height() / 1.5;
        tempElement.remove();

        images.each(function() {
            var self = $(this);
            self.on('mouseover', function() {
                if (this.naturalWidth > entryWidth ||
                        this.naturalHeight > 15 * emSize) {
                    self.addClass('expandable');
                } else {
                    self.removeClass('expandable');
                }
            }).on('click', function(event) {
                if (self.hasClass('expandable')) {
                    event.stopPropagation();
                    self.toggleClass('expanded');
                }
            });
        });

        $('body').on('click', function() {
            $('img.expanded').removeClass('expanded');
        });
    }
});
