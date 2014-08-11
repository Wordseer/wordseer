/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.store.LayoutStore', {
	extend: 'Ext.data.Store',
	storeId: 'LayoutStore',
	proxy: {
		type: 'memory',
		id: 'LayoutStore',
	},
	model: 'WordSeer.model.LayoutModel',
	autoSync:true,
	setCurrent: function(layout_model) {
		if (this.getCurrent()) {
			this.getCurrent().set('is_current', false);
		}
		layout_model.set('is_current', true);
		this.current = layout_model;
	},
	getCurrent: function() {
		return this.current;
	}
})