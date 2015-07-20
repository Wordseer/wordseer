/**
The sentence menu that appears when the user mouses over a sentence in a sentence
list.
*/
Ext.define('WordSeer.view.menu.ResultListMenu', {
	extend: 'WordSeer.view.menu.Menu',
	requires: [
		'WordSeer.view.menu.SetMenu',
	],
	alias: 'widget.result-list-menu',
	config: {
		/**
		@cfg {Integer} sentenceID The ID of the sentence to open.
		*/
		sentenceId: false,

		/**
		@cfg {Integer} documentID The ID of the document to open.
		*/
		documentId: false,

		/**
		@cfg {String} type Whether these search results are documents or
		sentences. Either 'sentence' for sentences, or 'document' for document.
		*/
		type: 'sentence',

		/**
		@cfg {Boolean} seeInContext Whether or not to show the 'See in context'
		option.

		*/
		seeInContext: true,
	},
	width: 150,

	initComponent: function() {
		var me = this;
		var itemIds = [(me.getType() === 'sentence'? me.getSentenceId()
						: me.getDocumentId())+""];
		var items = [];
		if (me.seeInContext) {
			items.push({
				xtype: 'wordseer-menuitem',
				action: 'open-document',
				text: (me.getType() === 'sentence')? 'See in context'
					: 'Open document',
			});
		}
		// var sets_store = me.getType() == 'sentence' ?
		// Ext.getStore('SentenceSetStore')
		// : Ext.getStore('DocumentSetStore');

		// items.push({
		// 	xtype: 'wordseer-menuitem',
		// 	menu: {
		// 		xtype: 'set-menu',
		// 		store: sets_store,
		// 		type: 'add',
		// 		ids: itemIds
		// 	},
		// 	text: 'Add to set...'
		// });

		// remove_from_set_options = [];
		// sets_store.getRootNode().cascadeBy(function(set) {
		// 	if (!set.isRoot()) {
		// 		if (set.get('ids').filter(function(x){
		// 			return x.id == itemIds[0];
		// 		}).length > 0) {
		// 			remove_from_set_options.push(set);
		// 		}
		// 	}
		// });
		// if (remove_from_set_options.length > 0) {
		// 	items.push({
		// 		xtype: 'wordseer-menuitem',
		// 		menu: {
		// 			xtype: 'set-menu',
		// 			store: sets_store,
		// 			type: 'remove',
		// 			ids: itemIds
		// 		},
		// 		text: 'Remove from set...'
		// 	});
		// }
		me.items = items;
		me.callParent(arguments);
	}
});
