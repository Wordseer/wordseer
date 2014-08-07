// When an element with the class "check-all" is clicked, all checkboxes in its
// table will be selected. On the second time, deselected, and so on.

$('.check-all').click(function () {
    var checked = $(this).data('checked');
    $(this).closest('table').find(':checkbox').prop('checked', !checked);
    $(this).data('checked', !checked);
});

