// Given a table in which the rows have checkboxes, allow the user to click
// anywhere on the row to activate the checkbox.

$('.click-anywhere tr').click(function (e) {
    if(!$(e.target).is('td input:checkbox') && !$(e.target).is('th') )
    $(this).find('input:checkbox').trigger('click');
});

// This function makes sure that the user can click on links in the trs.

$('.click-anywhere a').click(function (e) {
    e.stopPropagation();
});
