/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
*/
Ext.define('WordSeer.view.windowing.viewport.HboxLayout', {
	extend: 'WordSeer.view.windowing.viewport.Layout',
	id: 'single',
	alias: 'widget.hbox-layout',
	cls: 'background',
	layout: {
		type: 'hbox',
		align: 'stretch',
		reserveScrollbar: 'true',
		flex: 1,
	},
	initComponent: function() {
		if (this.getLayoutModel()) {
			// var main_panel = this.getLayoutModel().panels().getById("0");
			// this.items = [
			// 	{
			// 		xtype: 'layout-panel',
			// 		flex: 1,
			// 		layoutPanelModel: main_panel,
			// 		collapsible: false,
			// 		itemId: main_panel.get('id'),
			// 		items: [],
			// 	},
			// ];
		}
		this.callParent(arguments);
	},

	addPanel: function(panel_id) {
		var new_id = panel_id || Ext.id();
		var new_panel = Ext.create('WordSeer.model.LayoutPanelModel', {
			id: new_id,
			layout_id: this.getLayoutModel().get('id'),
			name: 'New Panel',
		});
		this.getLayoutModel().panels().add(new_panel);
		Ext.getStore('LayoutStore').sync();
		var items = [];
		if (this.items.items.length > 0) {
			items.push({
				xtype:'splitter',
				collapsible: false,
				itemId: new_panel.get('id')+"splitter",
			});
		}
		items.push({
			xtype: 'layout-panel',
			flex: 1,
			layoutPanelModel: new_panel,
			itemId: new_panel.get('id'),
			items: [],
			collapsible: false,
			collapseDirection:'left',
		});
		this.add(items);
		this.doLayout();
		return this.down('layout-panel[itemId='+new_panel.get('id')+"]");
	},

// 	TODO: panel is still in the DOM after it's removed
	removePanel: function(panel) {
		var id = panel.itemId;
		var panel_model = this.getLayoutModel().panels().getById(id);
		this.getLayoutModel().panels().remove(panel_model);
		panel.up().remove(id+"splitter", true);
		if (this.getLayoutModel().panels().getCount() == 1) {
			// If there's only one other panel right now, remove that panel's
			// splitter.
			var other_id = this.getLayoutModel().panels().getAt(0).get('id');
			panel.up().remove(other_id+"splitter", true);
		}
		panel.up().remove(id, true);
		this.setPanelActivationOrder();
	}
})
