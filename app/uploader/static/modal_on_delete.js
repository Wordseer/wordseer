//Call up a modal to confirm pressing a certain button. This is not yet
//functional.

$('button.confirm-delete').on('click', function(e){
    console.log("foo")
    var $form=$(this).closest('form');
    e.preventDefault();
    $('#confirmDelete').modal({ backdrop: 'static', keyboard: false })
        .one('click', '#confirm', function (e) {
            $form.trigger('submit');
        });
});