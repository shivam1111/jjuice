;(function($) {
    'use strict';

    // Check owlCarousel
    if (! $.fn.owlCarousel) {
        throw 'jQuery owlCarousel must loaded before the script.';
    }

    // Variable
    var $testimonials = $('.Awe_testimonial');

    // Render owlCarousel
    $testimonials.each(function() {
        var $carousel = $(this);
        var data = $carousel.data();

        // Default setting
        var sDefault = {
            items: 1,
            nav: true,
            dots: false
        };

        $carousel.owlCarousel($.extend(sDefault, data));
    });

})(jQuery);
