/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A list of the most frequent words in the sentences matching a
search query.
*/
Ext.define('WordSeer.store.FrequentWordsStore', {
	extend: 'Ext.data.Store',
	requires: [
		'WordSeer.model.WordModel'
	],
	autoDestroy: true,
	config: {
		/**
		@cfg {String} pos The part of speech of this list of frequent words.
		*/
		pos: 'N'
	},
	model: 'WordSeer.model.WordModel',
	proxy: {
		type: 'ajax',
		noCache: false,
		timeout: 9000000,
		url: ws_api_path + ws_project_path + project_id + '/words',
		reader: {
			type: 'json',
			root: 'results'
		},
		extraParams: {
			instance: getInstance(),
			user: getUsername()
		},
	},
	sorters: [{property: "count", direction: "DESC"}],
	constructor: function(config) {
		this.callParent(arguments);
		this.getProxy().setExtraParam('user', getUsername());
	}
});
