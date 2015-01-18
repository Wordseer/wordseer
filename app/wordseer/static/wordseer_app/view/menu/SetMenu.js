/**
A menu showing a options for adding or removing given items from the sets that
exist of that type.
*/
Ext.define('WordSeer.view.menu.SetMenu', {
	extend: 'WordSeer.view.menu.Menu',
	alias: 'widget.set-menu',
	requires: [
		'WordSeer.view.menu.SetMenuItem',
		'WordSeer.view.menu.CreateAndAddMenuItem',
	],
	config: {
		/**
		@cfg {String} type The type of this menu -- either 'add' or 'remove'.
		*/
		type: '',

		/**
		@cfg {WordSeer.store.DocumentSetsStore|SentenceSetStore|PhraseSetStore} store
		The store containing the sets.
		*/
		store: false,

		/**
		@cfg {Array} ids The item ID's of the sentences, documents, or words
		to add or remove.
		*/
		ids: []
	},
	minWidth: 100,
	initComponent: function() {
		var me = this;
		var items = [];
		if (me.getType() === 'add') {
			items.push({
				xtype: 'create-and-add-menuitem',
				ids: me.getIds(),
				store: me.getStore(),
			});
		}
		me.getStore().getRootNode().cascadeBy(function(set) {
			if (!set.isRoot()) {
				if (me.getType() === 'add' || (me.getType() === 'remove' &&
					me.setContainsItems(set))) {
					var menuitem = {
						xtype: 'set-menuitem',
						action: me.getType(),
						text: '',
						record: set,
						store: me.getStore(),
						items: me.getIds()
					};
					if (set instanceof WordSeer.model.PhraseSetModel) {
						menuitem.menu = [{
							xtype: 'set-menuitem',
							text: set.get('phrases').join(", "),
							action: 'open',
							record: set,
							store: me.getStore(),
							items: me.getIds()
						}];
					}
					items.push(menuitem);
				}
			}
		});
		me.items = items;
		me.callParent(arguments);
	},

	setContainsItems: function(set) {
		var me = this;
		if (set instanceof WordSeer.model.PhraseSetModel) {
			return set.get('phrases').filter(function(phrase) {
				return me.getIds().indexOf(phrase) != -1;
			}).length > 0;
		} else {
			return set.get('ids').filter(function(x){
				return me.getIds().indexOf(x.id) != -1;}).length > 0;
		}
	}
});
