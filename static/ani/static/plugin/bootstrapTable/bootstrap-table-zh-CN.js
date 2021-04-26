/**
 * Bootstrap Table Chinese translation
 * Author: Zhixin Wen<wenzhixin2010@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['zh-CN'] = {
        formatLoadingMessage: function () {
            return 'Loading……';
        },
        formatRecordsPerPage: function (pageNumber) {
            return ' ' + pageNumber + ' records per page';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Show ' + pageFrom + ' to ' + pageTo + ' records，total ' + totalRows + ' records';
        },
        formatSearch: function () {
            return 'Search';
        },
        formatNoMatches: function () {
            return 'No Data';
        },
        formatPaginationSwitch: function () {
            return 'Page Turning';
        },
        formatRefresh: function () {
            return 'Refresh';
        },
        formatToggle: function () {
            return 'Switch';
        },
        formatColumns: function () {
            return 'Column';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['zh-CN']);

})(jQuery);