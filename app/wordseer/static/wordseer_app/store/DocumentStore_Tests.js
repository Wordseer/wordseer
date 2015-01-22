/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */StartTest(function(t){
	t.diag("Checking Document Store");
	t.requireOk('WordSeer.store.DocumentStore', function() {
		var store = Ext.create('WordSeer.store.DocumentStore');
		store.load({
			scope: this,
			callback: function(records, operation, success) {
				console.log(records);
				t.is(success, true, 'Read records');
				t.is(records.length, 6, 'correct number of records received');
				t.is(store.getCount(), 6, 'All documents loaded');
				t.isNot(store.getById(1).get('title'), undefined, 'Documents loaded ok');
			}
		});
	})
})