/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.store.PhrasesStore', {
	extend: 'Ext.data.Store',
	model: 'WordSeer.model.PhraseModel',
	remoteFilter: false,
	autoDestroy: true,
	proxy: {
		type: 'ajax',
		noCache: false,
		timeout: 9000000,
		url: ws_api_path + ws_project_path + project_id + '/sequences',
		reader: {
			type: 'json',
			root: 'results'
		},
		extraParams: {
			length: 2,
			has_function_words: 0
		},
	},
	filters: [{property:'lemmatized', value:0}]
});
