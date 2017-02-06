;(function($) {
    'use strict';

    // Check owlCarousel
    if (! $.fn.owlCarousel) {
        throw 'jQuery owlCarousel must loaded before the script.';
    }

    // Brands selector
    var $brands = $('.brands-carousel.owl-carousel, .Awe_image_carousel');

    // Render owlCarousel
    $brands.each(function() {
        var $carousel = $(this);
        var data = $carousel.data();

        var items = $carousel.data('items');

        // Settings
        var sDefault = {
            items: items ? items : 4,
            nav: true,
            dots: false,
            responsive:  {
                320: { items: 1 },
                480: { items: 2 },
                768: { items: 3 },
                992: { items: items ? items : 4 }
            }
        };

        $carousel.owlCarousel($.extend(sDefault, data));
    });

})(jQuery);
