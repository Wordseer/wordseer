$('.click-anywhere tr').click(function (e) {
    if(!$(e.target).is('td input:checkbox') && !$(e.target).is('th') )
    $(this).find('input:checkbox').trigger('click');
});

$('.click-anywhere a').click(function (e) {
    e.stopPropagation();
});
