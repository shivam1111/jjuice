;(function($) {
    'use strict';

    // Check owlCarousel
    if (! $.fn.owlCarousel) {
        throw 'jQuery owlCarousel must loaded before the script.';
    }

    // Variable
    var $products = $('.products.owl-carousel');

    // Render owlCarousel
    $products.each(function() {
        var $carousel = $(this);
        var data = $carousel.data();

        var items = $carousel.data('items');
        if (! items) items = 4;

        // Responsive
        var responsive = {};

        if (items == 4) {
            responsive = {
                0: { items: 1 },
                480: { items: 2 },
                768: { items: 3 },
                980: { items: 4 }
            };
        } else if (items == 3) {
            responsive = {
                0: { items: 1 },
                480: { items: 2 },
                768: { items: 2 },
                992: { items: 3 }
            };
        }

        // Default setting
        var sDefault = {
            margin: 30,
            nav: true,
            dots: false,
            items: items,
            responsive: responsive
        };

        $carousel.owlCarousel($.extend(sDefault, data));
    });

})(jQuery);
