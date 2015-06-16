/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A {@link WordSeer.view.wordmenu.WordMenu word menu} item to open a
{@link WordSeer.model.PhraseSetModel}.
*/
Ext.define("WordSeer.view.menu.SetMenuItem", {
	extend: "WordSeer.view.menu.MenuItem",
	alias:'widget.set-menuitem',
	config: {

		/**
		@cfg {String} action The action to take when this menu item is clicked.
		One of the following: 'add-to-set', 'open-set', 'remove-from-set'.
		*/
		action: false,

		/**
		@cfg {WordSeer.model.SubsetModel} record
		The set in question.
		*/
		record: false,

		/**
		@cfg Array[Number] item The identifier of the item that was
		clicked to produce this menu. In the case of documents and sentences,
		this is the sentence or document ID, in the case of words or phrases, it
		is the word or phrase;
		*/
		items: '',

		/**
		@cfg {WordSeer.store.DocumentSetListStore|WordSeer.store.SentenceSetListStore} store
		The store containing the set records.
		*/
		store: false,
	},
	constructor: function(cfg) {
		this.initConfig(cfg);
		if (this.record && this.text.length === 0) {
			if (this.record instanceof WordSeer.model.PhraseSetModel) {
				this.text = (this.record.get('text') + ' (' +
					this.record.get('phrases') .length +")");
			} else {
				this.text = (this.record.get('text') + ' (' +
					this.record.get('ids').length + ')');
			}

		}
		this.callParent(arguments);
	},
});
