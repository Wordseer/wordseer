/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Displays an overview of the most frequent nouns, verbs, adjectives and phrases
in the collection.
*/
Ext.define('WordSeer.view.overview.FrequentWordsOverview', {
	extend: 'WordSeer.view.overview.Overview',
	alias: 'widget.frequent-words-overview',
	title: 'Frequent Words',
	iconCls: 'frequent-words',
	items: [],
	initComponent: function() {
		this.items = [
			{
				xtype: 'tag-list',
				title: 'Phrases',
				tagField: 'sequence',
				numberFields: ['count'],
				store: this.getModel().getPhrasesStore()
			},
			{
				xtype: 'tag-list',
				title: 'Nouns',
				tagField: 'word',
				numberFields: ['count'],
				store: this.getModel().getNStore(),
			},
			{
				xtype: 'tag-list',
				title: 'Verbs',
				tagField: 'word',
				numberFields: ['count'],
				store: this.getModel().getVStore(),
			},
			{
				xtype: 'tag-list',
				title: 'Adjectives',
				tagField: 'word',
				numberFields: ['count'],
				store: this.getModel().getJStore(),
			},
		]
		this.callParent(arguments);
	    this.addListener('afterrender', function(me) {
	        me.populate();
	    });
	},
	populate: function() {
	    var me = this;
	}
});
