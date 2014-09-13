/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Holds a flat list of all the metadata that match a search query.
Used by the {@link WordSeer.view.metadata.MetadataComboBox}.
*/
Ext.define("WordSeer.store.MetadataListStore", {
	extend: 'Ext.data.Store',
	autoDestroy: true,
	model: 'WordSeer.model.MetadataModel',
	proxy: {
		type: 'ajax',
		noCache: false,
		url: ws_project_path + project_id + '/properties',
		extraParams: {
			user: getUsername(),
		},
		reader: {
          type: 'json',
          root: 'results',
      },
	},
	sorters: [{property:'count', direction: 'DESC'}],
	constructor: function(config) {
		this.callParent(arguments);
		this.getProxy().setExtraParam('user', getUsername());
	}
});
