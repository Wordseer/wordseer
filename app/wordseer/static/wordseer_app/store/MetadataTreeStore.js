/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Holds a flat list of all the metadata that match a search query.
Used by the {@link WordSeer.view.metadata.MetadataComboBox}.
*/
Ext.define("WordSeer.store.MetadataTreeStore", {
	extend: 'Ext.data.TreeStore',
	autoDestroy: true,
	clearOnLoad: true,
	model: 'WordSeer.model.MetadataModel',
	proxy: {
		type: 'ajax',
		noCache: false,
		url: ws_project_path + project_id + '/properties',
		extraParams:{
			view: "tree"
		},
		reader: {
			type:'json',
			root: 'children',
		},
	},
	sorters: [{property:'text', direction:'ASC'}],
	constructor: function(config) {
		this.callParent(arguments);
	},
});
