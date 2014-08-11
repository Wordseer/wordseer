/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.model.LayoutModel', {
	requires: 'WordSeer.model.LayoutPanelModel',
	extend: 'Ext.data.Model',
	fields: [
		{type: 'string', name: 'id'},
		{type: 'string', name: 'name'},
		{type: 'boolean', name: 'is_current', default: false},
		{type: 'string', name: 'viewport_view'},
		{type: 'string', name: 'thumbnail_view'},
	],
	hasMany: {
		model:'WordSeer.model.LayoutPanelModel',
		name: 'panels',
		foreignKey: 'layout_id',
		storeConfig: {
			autoSync: true,
			proxy: {
				type: 'memory'
			}
		}
	},
	addHistoryItemToPanel: function(history_item, panel_id) {
		this.panels().getById(panel_id).addHistoryItem(history_item);
	}
})
