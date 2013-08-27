$(document).ready(function() {
    var images = $('div.hero > img'), i = 0;
    if (images.length > 1)
        setInterval(function() {
            var j = i;
            i = (i + 1) % images.length;
            images.eq(j).addClass('prev');
            images.eq(i).removeClass('next');
            setTimeout(function() {
                images.eq(j).removeClass('prev').addClass('next');
            }, 1000);
        }, 10000);
});
