/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */StartTest(function(t){
	t.diag("Checking User Controller");
	t.requireOk('Account.controller.User', function() {
		var controller = Ext.create('Account.controller.User');
		t.isNot(controller.getUsersStore(), undefined, 'User store exists.');
	})
})