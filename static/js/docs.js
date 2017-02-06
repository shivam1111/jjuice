'use strict';

function aweDocsListIcons(el) {
    var settings = { valueNames: ['doc-list-class'], page: 750 };
    var list = new List(el, settings);
}

function aweDocsBackgroundHeight() {
    var resizeTimer;

    var backgroundHeight = $(window).height() - 80;

    $('.background').height(backgroundHeight);

    $(window).on('resize', function(e) {
        clearTimeout(resizeTimer);

        resizeTimer = setTimeout(function() {
            $('.background').height(backgroundHeight);
        }, 250);
    });
}
