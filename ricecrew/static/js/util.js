util = {
    touchSupported: 'ontouchend' in document,

    clamp: function(x, min, max) {
        return (x < min) ? min : ((x > max) ? max : x);
    }
};
