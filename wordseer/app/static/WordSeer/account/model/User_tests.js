/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */StartTest(function(t){
	t.diag("Checking User Model");
	t.requireOk('Account.model.User', 'Account.model.Instance', function() {
		var data = {
			id: 1,
			username: 'test',
			instances: [
				{
					id: 1,
					name: 'test_instance',
					user_id: 1,
					creation_date_ms: 123456,
					is_new: false,
				}
			]
		}
		var user = new Account.model.User(data);
		t.is(user.get('username'), data.username,
			'Instantiate username from data');
		t.is(user.get('id'), data.id, 'Instantiate id from JSON');
		t.isNot(user.instances, undefined, 'instances() method exists.')
		t.isNot(user.addInstances, undefined, 'addInstances() method exists.')
		user.addInstances(data.instances);
		var instances = user.instances();
		t.is(instances.getCount(), data.instances.length, 'Instances initialized');
		
	})
})