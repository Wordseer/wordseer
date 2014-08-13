/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Displays an overview of the most frequent nouns, verbs, adjectives and phrases
in the collection.
*/
Ext.define('WordSeer.view.overview.MetadataOverview', {
	extend: 'WordSeer.view.overview.Overview',
	requires: [
		'WordSeer.view.overview.TagListOverview',
		'WordSeer.view.metadata.facet.RangeFacet',
	],
	alias: 'widget.metadata-overview',
	title: 'Metadata',
	iconCls: 'metadata',
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
			if (!me.store.getRootNode()) {
				me.store.load();
			} else {
				me.drawn = false;
				me.redraw();
			}
		});
	},
	redraw: function() {
		var me = this;
		if (!me.drawn) {
			me.drawn = true;
			var store = this.model.getMetadataTreeStore();
			Ext.suspendLayouts();
			me.removeAll();
			store.getRootNode().childNodes.forEach(function(child) {
				if (child.get('type') == 'string' &&
					child.get('propertyName').indexOf('_set') == -1) {
					var property = child.get('propertyName');
					me.add({
						xtype: 'tag-list',
						store: me.model.getMetadataListStore(),
						title: child.get('text'),
						tagField: 'text',
						numberFields: ['document_count'],
						filterFn: function(record) {
							return record.get('propertyName') == property;
						}
					});
				} else  if (child.get('propertyName').indexOf('_set') == -1) {
					me.add({
						xtype: 'rangefacet',
						info: child,
						title: child.get('displayName'),
						itemId: child.get('propertyName'),
						listeners: {
							afterrender: function(view) {view.draw();}
						}
					});
				}
			});
			Ext.resumeLayouts(true);
		}
	}
});
