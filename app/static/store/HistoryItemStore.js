/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A central, shared store for keeping track of the user's search history. The
storeId of this store is `HistoryItemStore`. There is always only one instance 
of this store. It can be accessed using `Ext.getStore("HistoryItemStore")`. It
is instantiated and controlled by the 
{@link WordSeer.controller.HistoryController}.
*/
Ext.define('WordSeer.store.HistoryItemStore', {
	extend: 'Ext.data.Store',
	storeId: 'HistoryItemStore',
	config: {
		/** @cfg {WordSeer.model.HistoryItemModel} current The most recent
		history item.
		*/
		current: false,
	},
	proxy: {
		type: 'localstorage',
		id: 'HistoryItemStore',
		writer: 'xml',
		reader: 'xml',
	}, 
	model: 'WordSeer.model.HistoryItemModel',

	/** Sets the most recent history item to the given 
	{@link WordSeer.model.HistoryItemModel HistoryItemModel} instance. Called
	by the {@link WordSeer.controller.SearchController#newHistoryItem} method
	when the user performs a new search or changes search parameters.
	
	@param {WordSeer.model.HistoryItemModel} history_item The history item
	to set as the current one.
	*/
	setCurrent: function(history_item) {
		if (history_item) {			
			if (this.getCurrent()) {
				this.getCurrent().set('is_current', false);
			}
			history_item.set('is_current', true);
		}
		this.current = history_item;
	},
	
	/** Returns the most recent history item.
	@return {WordSeer.model.HistoryItemModel} The most recent history item.
	*/
	getCurrent: function() {
		return this.current;
	}
})