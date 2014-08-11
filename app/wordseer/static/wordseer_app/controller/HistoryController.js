/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Manages actions related to viewing and replaying items from the user's
search history. Controls the following views:

	- {@link WordSeer.view.history.HistoryList}

The display and arrangement of new layout panels is managed by the
{@link WordSeer.controller.WindowingController}. This controller just manages
interactions with the history list display, which allows the user to view their
history of searches, and to choose a subset of them to view side by side.
*/
Ext.define('WordSeer.controller.HistoryController', {
	extend: 'Ext.app.Controller',
	views: [
		'history.HistoryList'
	],
	stores: [
		'HistoryItemStore',
	],
	init: function() {
		Ext.getStore('HistoryItemStore').sort('creation_timestamp', 'DESC');
		this.control({
			'button[action=show-history]': {
				click: function() {
					Ext.ComponentQuery.query('history-list').toggle();
				}
			},
			'history-list' :{
				select: this.displayHistoryItem,
				deselect: this.hideHistoryItem,
			}
		})
	},

	/** Creates a new {@link WordSeer.model.HistoryItemModel} representing
	the passed-in search parameters.

	@param {WordSeer.model.FormValues} formValues A
	formValues object representing a search query.
	*/
	newHistoryItem: function(formValues) {
		var history_item = Ext.create('WordSeer.model.HistoryItemModel', {
			formValues: formValues.serialize(),
			widget_xtype: formValues.widget_xtype,
			id: Date.now().toString(),
			creation_timestamp: new Date(),
			last_viewed_timestamp: new Date(),
			is_current: true
		});
		var store = Ext.getStore('HistoryItemStore');
		store.insert(0, history_item);
		store.setCurrent(history_item);
		store.sync();
//		console.log(store.count());
		return history_item;
	},

	/** Adds a layout panel that depicts the
	{@link WordSeer.model.HistoryItemModel HistoryItemModel} to the
	Layout, but only if it is not already in view.

	@param {WordSeer.view.history.HistoryList} history_list_view
		The HistoryList instance that was clicked.
	@param {WordSeer.model.HistoryItemModel} history_item The
		selected history item from the history list.
	*/
	displayHistoryItem: function(history_list_view, history_item) {
		// Check that the history item does not already have a layout panel
		// displaying it.
		if (history_item.get('layout_panel_id') == "") {
			var direction = "east";
			var layout_panel = this.getController(
					'WindowingController')
				.addPanel(direction);
			var layout_panel_model = layout_panel
				.getLayoutPanelModel();
			var id = history_item.get('id');
			var history_items = layout_panel_model.get(
				'previous_history_items');
			var index = history_items.indexOf(id);
			if (index == -1) {
				Ext.getStore('LayoutStore').getCurrent()
					.addHistoryItemToPanel(history_item,
						layout_panel.itemId);
			}
			Ext.defer(function(layout_panel, layout_panel_model, id){
				this.getController('WindowingController')
					.playHistoryItem(layout_panel, layout_panel_model,
							id);
			}, 1000, this, [layout_panel, layout_panel_model, id]);
		}
	},

	/** Removes the
	{@link WordSeer.view.windowing.viewport.LayoutPanel layout panel}
	that depicts the un-selected history item from the Layout and resets the
	layout_panel_id of the un-checked history item to ''.

	@param {WordSeer.view.history.HistoryList} history_list_view
		The HistoryList instance that was clicked.

	@param {WordSeer.model.HistoryItemModel} history_item The
		un-selected history item from the history list.
	*/
	hideHistoryItem: function(history_list_view, history_item) {
		// remove the history item from the layout.
		var layout_panel_id = history_item.get('layout_panel_id');
		var panel = Ext.ComponentQuery.query(
			'layout-panel[itemId=' + layout_panel_id + ']')[0];
		if (panel) {
			this.getController('WindowingController')
				.removePanel(panel)
		}
		history_item.set('layout_panel_id', '');
	},

	/** Checks the history item with the given ID in the
	{@link WordSeer.view.history.HistoryList} view. Does not trigger the
	{@link WordSeer.view.history.HistoryList#select} event.

	@param {String} history_item_id The ID of the history item to check.
	*/
	selectHistoryItem: function(history_item_id) {
		if (history_item_id) {
			history_list_view =	Ext.getCmp('historylist');
			// Select the new history item, but pass in 'true' and 'true' to
			// preserve the previously selected items, and suppress the
			// selection event respectively.
			history_item = Ext.getStore('HistoryItemStore').getById(
				history_item_id);
			if (history_list_view) {
				history_list_view.select(history_item,
					true, true);
			}
		}
	},

	/** Un-checks the history item with the given ID in the
	{@link WordSeer.view.history.HistoryList} view. Only triggers the
	{@link WordSeer.view.history.HistoryList#deselect} event if fire_event
	is true.

	@param {String} history_item_id The ID of the history item to uncheck.
	@param {Boolean} fire_event Whether or not to fire the deselect
	event in the HistoryList. If this is true, the event is not triggered and
	{@link #hideHistoryItem} gets called as a result.
	*/
	deselectHistoryItem: function(history_item_id, fire_event) {
		if (history_item_id) {
			var history_item = Ext.getStore('HistoryItemStore').getById(
				history_item_id);
			history_list_view =	Ext.getCmp('historylist');
			// Suppress the deselect event by passing in true as the second
			// parameter.
			if (history_list_view) {
				history_list_view.deselect(history_item,
					fire_event? false : true);
			}
		}
	},
})
