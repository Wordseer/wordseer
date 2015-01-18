/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Displays a pop-up showing the most frequent nouns verbs and adjectives that
occur near a word or phrase or word set. Accessed through the
{@link WordSeer.view.wordmenu.WordMenu}.
*/
Ext.define('WordSeer.view.relatedwords.SynsetPopup', {
	extend: 'WordSeer.view.box.Overlay',
	alias: 'widget.synsets-popup',
	requires: [
		'WordSeer.view.relatedwords.SynsetList'
	],
	config: {
		/** @cfg {Object} data The list of synonym words */
		data: {},

		/** @cfg {WordSeer.model.WordModel} current The word or
		{@link WordSeer.model.PhraseModel} for which these related words are
		being shown. */
		current:{},
	},
	destroyOnClose: true,
	draggable: true,
	constrain: true,
	width: 230,
	height: 300,
	layout: 'fit',
	initComponent: function() {
		var items = [];
		items.push({
			xtype: 'synset-list',
			data: this.getData(),
			title: 'Words that occur in similar contexts to ' +
			this.getCurrent().get('word')
		});
		this.items = items;
		this.callParent(arguments);
	}
});
