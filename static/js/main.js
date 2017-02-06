'use strict';

if (window.jQuery) var $ = window.jQuery;

$(function () {
    aweHosoren.init();

    //== DEMO ONLY
    aweSearchMenubar();
    aweQuickViewProduct();
});

function aweMaps(mapElement) {
    if (! mapElement) {
        mapElement = '#contact-map';
    }

    var map = new GMaps({
        el: mapElement,
        lat: $(mapElement).data('lat'),
        lng: $(mapElement).data('lng'),

        draggable: true,
        scrollwheel: false
    });

    map.addMarker({
        lat: $(mapElement).data('lat'),
        lng: $(mapElement).data('lng'),
    });
}

// ===
function aweSearchMenubar() {
    var $navbar = $('.awemenu-nav');

    var $searchForm = $('#menubar-search-form');
    var $openSearch = $('#open-search-form');
    var $closeSearch = $('#close-search-form');

    $openSearch.on('click', function(e) {
        e.preventDefault();
        $searchForm.toggleClass('open');

        setTimeout(function() {
            $searchForm.find('input').focus();
        }, 250);
    });

    $closeSearch.on('click', function(e) {
        e.preventDefault();
        $searchForm.removeClass('open');
    });

    $searchForm.keyup(function(e) {
        if (e.keyCode == 27 && $searchForm.hasClass('open')) {
            $searchForm.removeClass('open');
        }
    });

    $(window).resize(function() {
        if ($navbar.hasClass('awemenu-mobile')) {
            $searchForm.width('100%');
            $searchForm.css({right: '0'});
        } else {
            var $awemenu = $('.awemenu-nav .awemenu');
            var $aweicon = $('.awemenu-nav .navbar-icons');

            var width = $awemenu.width() + 50;
            var offsetRight = $aweicon.width() + 20;

            $searchForm.width(width);
            $searchForm.css({right: offsetRight});
        }
    }).trigger('resize');

}

function aweQuickViewProduct() {
    $('.product-quick-view').magnificPopup({
        type: 'ajax'
    });
}

// ===
function aweMainSlider() {
    var $slider = $('.main-slider');

    $slider.owlCarousel({
        items: 1,
        nav: true,
        dots: true,
        onInitialized: function() {
            $slider.find('.owl-item').each(function() {
                var $owlItem = $(this);

                var $mainSlide = $owlItem.find('.main-slider-item');
                var $mainImage = $owlItem.find('.main-slider-image > img');

                if ($mainSlide.length && $mainImage.length) {
                    $mainSlide.addClass('background');
                    $mainSlide.css('background-image', 'url('+$mainImage.attr('src')+')');

                    $mainImage.css({
                        opacity: 0,
                        visibility: 'hidden'
                    });
                }
            });
        }
    });
}

function awePriceSlider($selector) {
    if (! $selector) {
        $selector = $('#price-slider');
    }

    $selector.slider({
        values: [35, 250],
        min: 10,
        max: 320,
        step: 10,
        range: true,
        slide: function(e, ui) {
            $('#amount').text('$'+ui.value);
        }
    });
}

function aweBlogMasonry($selector) {
    if (! $selector) {
        $selector = $('.blog-masonry .row-masonry');
    }

    $selector.imagesLoaded(function() {
        $selector.masonry({
            itemSelector: '.column',
            columnWidth: '.column'
        });
    });
}

function aweProfolioIsotope($selector) {
    if (! $selector) {
        $selector = $('.grid');
    }

    $selector.imagesLoaded(function() {
        var $grid = $selector.isotope({
            itemSelector: '.grid-item',
            layoutMode: 'masonry'
        });
    });

    $('.awe-nav').on('click', 'a', function(e) {
        e.preventDefault();

        $(this).parents('.awe-nav').find('li').removeClass('active');
        $(this).closest('li').addClass('active');

        var filter = $(this).attr('data-filter');
        $selector.isotope({ filter: filter });
    });
}

function aweProfolioDetail() {
    $('.lasted-portfolio-carousel').owlCarousel({
        items: 4,
        nav: true,
        dots: false,
        margin: 30,
        responsive: {
            0: { items: 1 },
            480: { items: 2 },
            768: { items: 3 },
            980: { items: 4 }
        }
    });

    $('.image').magnificPopup({
        type: 'image',
        delegate: 'a',
        gallery: { enabled: true }
    });
}

function aweProductSidebar() {
    var $filterSidebar = $('#shop-widgets-filters');
    var $toggleButton = $('#open-filters');

    var $overlay = $('body').find('.widgets-filter-overlay');

    function _open() {
        $filterSidebar.addClass('open');

        if (! $overlay.length) {
            $('body').append('<div class="widgets-filter-overlay"></div>');
        }

        $('body').addClass('open-filters-open');
    }

    function _close() {
        $filterSidebar.removeClass('open');
        $(document).find('.widgets-filter-overlay').remove();
        $('body').removeClass('open-filters-open');
    }

    $toggleButton.on('click', function() {
        if (! $filterSidebar.hasClass('open')) {
            _open();
        } else {
            _close();
        }
    });

    $('body').on('click', '.widgets-filter-overlay', function() {
        _close();
    });
}

function aweProductRender(thumbHorizontal) {
    if (Modernizr && ! Modernizr.touch) {
        $('.easyzoom').easyZoom();
    }

    var sMain = new Swiper('.product-slider-main', {
        loop: false,

        nextButton: '.swiper-button-next',
        prevButton: '.swiper-button-prev'
    });

    var sThumb = new Swiper('.product-slider-thumbs', {
        loop: false,
        centeredSlides: true,
        spaceBetween: thumbHorizontal ? 15 : 0,
        slidesPerView: thumbHorizontal ? 4 : 3,
        direction: thumbHorizontal ? 'horizontal' : 'vertical',
        slideToClickedSlide: true
    });

    sMain.params.control = sThumb;
    sThumb.params.control = sMain;
}
