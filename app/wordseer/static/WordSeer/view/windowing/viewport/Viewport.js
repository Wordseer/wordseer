/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** The base container for the user's browser windows. All layout and control
components go in here. This container has two dockedItems:

- {@link WordSeer.view.windowing.viewport.TopBar} which contains the search bar
and other controls.
- {@link WordSeer.view.history.HistoryList} which displays and controls the
user's activity history.
*/
Ext.define('WordSeer.view.windowing.viewport.Viewport', {
	extend: 'Ext.panel.Panel',
	requires: [
		'WordSeer.view.windowing.viewport.TopBar',
		'WordSeer.view.history.HistoryList',
	],
	id: 'windowing-viewport',
	alias: 'widget.windowing-viewport',
	config: {
		layoutModel: false,
	},
	layout: 'fit',
	tbar: [
	 	{xtype: 'widgets-menu'},
   		     '-',
        {xtype:'universal-search-form'},
        '-',
        {xtype:'user-button'},
	],
	initComponent: function() {
		this.addEvents('setchanged');
		this.callParent(arguments);
	},
	/** Changes the {@link WordSeer.model.LayoutModel} associated with
	this view and instantiates the new layout within this viewport.
	@param {WordSeer.model.LayoutModel} layout_model The new layout model to
	associate with this view.
	*/
	addLayout: function(layout_model) {
		var layout = this.add(Ext.create(layout_model.get('viewport_view'),{
			layoutModel: layout_model
		}))
		return layout;
	}

})
