/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Displays an overview of the most frequent nouns, verbs, adjectives and phrases
in the collection.
*/
Ext.define('WordSeer.view.overview.SetsOverview', {
	extend: 'WordSeer.view.overview.Overview',
	alias: 'widget.sets-overview',
	title: 'Sets',
	iconCls: 'Sets',
	items: [],
	initComponent: function() {
		var me = this;
		me.store = me.model.getMetadataTreeStore();
		me.callParent(arguments);
		me.addListener('afterrender', function(me) {
			me.store.addListener('load', function() {
				me.redraw();
				me.model.getMetadataListStore().load();
			});
			me.store.load();
		});
	},

	redraw: function() {
		var me = this;
		if (! me.drawn) {
			me.drawn = true;
			var store = this.model.getMetadataTreeStore();
			me.removeAll();
			store.getRootNode().childNodes.forEach(function(child) {
				if (child.get('type') == 'string' &&
					child.get('propertyName').indexOf('_set') != -1) {
					var property = child.get('propertyName');
				me.add({
					xtype: 'tag-list',
					store: me.model.getMetadataListStore(),
					title: child.get('text'),
					tagField: 'text',
					numberFields: ['count'],
					filterFn: function(record) {
						return record.get('propertyName') == property;
					}
				});
			}
			});
			me.doLayout();
		}
	}
});
