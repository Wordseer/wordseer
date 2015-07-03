/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** The base class for all layout managers. The functions of a layout manager
are:
- Keeping track of the the open {@link WordSeer.view.windowing.layout.LayoutPanel}s
- Adding and removing LayoutPanels
- Keeping track of the order in which the panels were last activated.
*/
Ext.define('WordSeer.view.windowing.viewport.Layout', {
	extend: 'Ext.Container',
	alias: 'widget.layout',
	requires: [
		'WordSeer.view.windowing.viewport.LayoutPanel',
	],
	layout: 'fit',
	/** @cfg {WordSeer.model.LayoutModel} layoutModel The model representing
	the data for this layout. It contains the id of this layout and a
	list of {@link WordSeer.model.LayoutPanelModel}s corresponding to the panels
	currently being displayed.
	*/
	config: {
		layoutModel: false,
	},
	initComponent: function() {
		this.callParent(arguments);
		this.setPanelActivationOrder();
	},
	/** Resets the list representing the panel activation order.
	*/
	setPanelActivationOrder: function() {
		var me = this;
		this.panel_activation_order = [];
		this.query('layout-panel').forEach(function(item) {
			me.panel_activation_order.push(item.itemId);
		})
	},
	/** Returns the {@link WordSeer.view.windowing.viewport.LayoutPanel}
	in this layout that has the given ID

	@param {Number} id The id of the layout panel to retrieve.
	@return {@link WordSeer.view.windowing.viewport.LayoutPanel} The panel with
	the given ID.
	*/
	getPanel: function(id) {
		return this.query(
			'layout-panel[itemId='+id+']')[0];
	},
	/** Returns the most recently activated
	{@link WordSeer.view.windowing.viewport.LayoutPanel} in this layout.

	@return {@link WordSeer.view.windowing.viewport.LayoutPanel} the most
	recently activated layout panel
	*/
	getCurrentPanel: function() {
		return this.getPanel(this.panel_activation_order[0]);
	},

	/** Returns the second-most-recently activated
	{@link WordSeer.view.windowing.viewport.LayoutPanel} in this layout.

	@return {@link WordSeer.view.windowing.viewport.LayoutPanel} the second-
	most-recently activated layout panel.
	*/
	getPreviousPanel: function() {
		if (this.panel_activation_order.length < 2) {
			return this.getPanel(this.panel_activation_order[0]);
		} else {
			return this.getPanel(this.panel_activation_order[1]);
		}
	},

	/** Adds a new empty {@link WordSeer.view.windowing.viewport.LayoutPanel} to
	the layout. This is an empty method that does nothing. Child classes must
	implement the details of this method. This is called by
	{@link WordSeer.controller.WindowingController#addPanel}.
	@return {WordSeer.view.windowing.viewport.LayoutPanel} The layout panel
	that was added */
	addPanel: function(){},

	/** Removes the given {@link WordSeer.view.windowing.viewport.LayoutPanel}
	from the layout. This is an empty method that does nothing. Child
	classes must implement this method. This is called by
	{@link WordSeer.controller.WindowingController#removePanel}.

	@param {@link WordSeer.view.windowing.viewport.LayoutPanel} panel The panel
	to remove.
	*/
	removePanel: function(){},
})
