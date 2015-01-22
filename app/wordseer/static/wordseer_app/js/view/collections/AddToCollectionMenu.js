/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A menu that appears when a user wants to add a selection of search results
to a collection. It shows a list of collections and a "new collection"
textfield.
*/
Ext.define("WordSeer.view.collections.AddToCollectionMenu", {
	extend: "Ext.menu.Menu",
	alias: 'widget.add-to-collection-menu',
	config: {
		/**
		@cfg {WordSeer.store.DocumentSetsStore
		| WordSeer.store.SentenceSetStore} store The data store that
		holds the list of collections.
		*/
		store: null,

		/**
		@cfg {Array} ids The list of id's to add to the collection.
		*/
		ids: [],
	},
	initComponent: function() {
		var store = this.getStore();
		var ids = this.getIds();
		if (store && ids.length > 0) {
	        var menu_items = [
	        	{
	        		xtype: 'textfield',
	        		action: 'create-and-add',
	        		value: 'New group',
	        		ids: ids,
	        		store: store,
	        	},
	        	'-'
	        ];
	        store.getRootNode().cascadeBy(function(record){
	        	if(!record.isRoot()){
		        		menu_items.push({
		        		xtype: 'menuitem',
		        		action: 'add-to-set',
		        		text: record.get('text') + " ("
		        			+ record.get('ids').length +")",
		        		subset_model: record,
		        		ids: ids,
		        	})
	        	}
	        	return true
	        }, this);

	        this.items = menu_items;
		}
		this.callParent(arguments);
	}
})
