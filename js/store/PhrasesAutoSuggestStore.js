/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Fetches autosuggest data from a URL and stores it.
*/
Ext.define('WordSeer.store.PhrasesAutoSuggestStore', {
	extend: 'Ext.data.Store',
	model: 'WordSeer.model.PhrasesAutoSuggestModel',
	autoDestroy: true,
	proxy: {
		type: 'ajax',
		noCache: false,
		timeout: 90000,
		url: '../../src/php/search-suggestions/autosuggest.php',
		extraParams: {
			instance: getInstance(),
			user: getUsername(),
		}
	}
});
