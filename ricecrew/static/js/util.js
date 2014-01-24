util = {
    touchSupported: 'ontouchend' in document,

    retinaSupported: window.devicePixelRatio && window.devicePixelRatio > 1,

    clamp: function(x, min, max) {
        return (x < min) ? min : ((x > max) ? max : x);
    }
};
