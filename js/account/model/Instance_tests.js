/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */StartTest(function(t){
	t.diag("Checking Instance Model");
	t.requireOk('Account.model.Instance', function() {
		var data = {
			id: 1,
			name: 'test_instance',
			creation_date_ms: 123456,
			user_id: 0,
		}
		var instance = Ext.create('Account.model.Instance', data);
		t.is(instance.get('name'), data.name, 'Instantiate fields from JSON');
		t.is(instance.get('id'), data.id, 'Instantiate fields from JSON');
		var date = new Date(data.creation_date_ms);
		t.is(instance.get('creation_date_ms'), date, 
			'Check Date instantiation');
	})
})