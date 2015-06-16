/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Controls all views related to autosuggest in the search bar.
*/
Ext.define('WordSeer.controller.AutoSuggestController', {
	extend: 'Ext.app.Controller',
	views: [
		'autosuggest.AutoSuggestMenu',
		'autosuggest.AutoSuggestMenuItem',
		'autosuggest.AutoSuggestTextField',
		'autosuggest.GrammaticalPhrasesOverlay',
		'autosuggest.PhrasesAutoSuggest',
		'autosuggest.PhrasesAutoSuggestMenuItem',
	],
	stores: [
		'PhrasesAutoSuggestStore',
	],
	models: [
		'PhrasesAutoSuggestModel',
	],

	init: function() {
//		console.log("Initialized autosuggest controller");
		this.control({
			'phrases-autosuggest-menuitem': {
				//highlight: this.showGrammaticalPhrasesOverlay
			}
		});
	},

	/**
	Displays the grammatical relations that this word has with other words.
	*/
	showGrammaticalPhrasesOverlay: function(menuitem) {
		Ext.ComponentQuery.query('grammatical-phrases-overlay').forEach(function(c) {
			c.close(10);
		});
		menuitem.focus();
		var query = menuitem.record.get('text');
		var record = menuitem.record;
		if (menuitem.record.get('class') == 'phrase-set') {
			query = menuitem.record.get('id');
		}
		if (menuitem.record.get('length') <= 1) {
			// true for one-word phrases and phrase sets
			Ext.Ajax.request({
				method: 'GET',
				url: ws_api_path +
					'search-suggestions/grammatical-relation-phrases/',
				params: {
					instance: getInstance(),
					user: getUsername(),
					query: query,
					type: menuitem.record.get('class')
				},
				callback: function(options, success, response) {
					var data = Ext.decode(response.responseText);
					var overlay = Ext.create(
						'WordSeer.view.autosuggest.GrammaticalPhrasesOverlay', {
							relations: data,
							shownBy: menuitem,
							record: record
					});
					overlay.showBy(menuitem, 'tl-tr?');
					menuitem.focus();
				}
			});
		}
	}
});
