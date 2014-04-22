// When an element with the id "check-all" is clicked, all checkboxes on the
// page will be selected. On the second time, deselected, and so on.

$('#check-all').click(function () {
    var checked = $(this).data('checked');
    $('form').find(':checkbox').attr('checked', !checked);
    $(this).data('checked', !checked);
});