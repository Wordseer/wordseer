/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A {@link WordSeer.view.wordmenu.WordMenu word menu} item to show contextual
actions for a phrase
*/
Ext.define("WordSeer.view.menu.PhraseMenuItem", {
	extend: "WordSeer.view.menu.MenuItem",
	alias:'widget.phrase-menu-item',
	config: {

		/**
		@cfg {String} text The phrase to search for.
		*/
		text: '',

		/**
		@cfg {Integer} phraseId The ID of this phrase
		*/
		phraseId: false,

		/**
		@cfg {Integer} phraseId The number of sentences in which this phrase
		appears.
		*/
		sentenceCount: 0,
	},
	initComponent: function() {
		var me = this;
		me.menu = [
			{
				text: 'See sentences ('+ me.sentenceCount +")",
				action: 'search-for-phrase',
			},
			// {
			// 	text: "<span class='wordmenu-label'>Add</span> to set",
			// 	menu: {
			// 		xtype: 'set-menu',
			// 		type: 'add',
			// 		store: Ext.getStore('PhraseSetStore'),
			// 		ids: [me.text]
			// 	}
			// }
		];
		// Are there any sets to which this phrase belongs? If so, give the
		// option to remove them.
		// sets_containing_this_phrase = [];
		// Ext.getStore('PhraseSetStore').getRootNode().cascadeBy( function(set) {
		// 		if (set.get('phrases').indexOf(me.phrase) != -1) {
		// 			sets_containing_this_word.push(set);
		// 		}
		// 	});
		// if (sets_containing_this_word.length > 0) {
		// 	me.menu.push({
		// 		text: "<span class='wordmenu-label'>Remove</span> from set",
		// 		menu: {
		// 			xtype: 'set-menu',
		// 			type: 'remove',
		// 			store: Ext.getStore('PhraseSetStore'),
		// 			ids: [me.text],
		// 		}
		// 	});
		// }
		this.callParent(arguments);
	}
});
