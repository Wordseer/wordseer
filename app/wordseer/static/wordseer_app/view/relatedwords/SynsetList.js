/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Holds the list of words of a given part of speech that most frequently
appear in sentences matching the main word. This view is used by the
{@link WordSeer.view.relatedwords.SynsetPopup}.
*/
Ext.define('WordSeer.view.relatedwords.SynsetList', {
	extend: 'WordSeer.view.overview.TagListOverview',
	alias: 'widget.synset-list',
	config: {
		/**
		@cfg {Array} data The data to be displayed, a list of words
		{id: word: score:}.
		*/
		data:[],
	},
	tagField: 'word',
	initComponent: function() {
		this.store = new Ext.data.Store({
			fields: [
				{type:'number', name: 'score'},
				{type:'string', name: 'word'},
				{type:'string', name: 'id'},
				{type:'string', name:'class', defaultValue:'word'},
				{type: 'string', name:'phrase_set', defaultValue:''},
			],
			data: this.getData()
		});
		this.callParent(arguments);
	},
});
