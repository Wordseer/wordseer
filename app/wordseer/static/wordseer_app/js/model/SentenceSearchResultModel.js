/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.model.SentenceSearchResultModel', {
	extend: 'Ext.data.Model',
	statics: {
		/** Returns a list of fields that should not be used as columns in a
		table or list.For use by views that want to display an instance of this
		model in a list or table.
		@return An array of strings: the names of the fields that should not be
		used as columns.
		*/
		getBaseFieldNames: function() {
			return ['sentence', 'id', 'document_id', 'sentence_set', 'phrase_set'];
		}
	},
	fields:[
		{name:'sentence', type: 'auto'},
		{name: 'id', type:'int'},
		{name: 'document_id', type: 'int'},
		{name: 'sentence_set', type: 'string', defaultValue:""},
	],
});

