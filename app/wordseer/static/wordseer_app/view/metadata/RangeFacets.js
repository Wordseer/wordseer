/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Displays an overview of the most frequent nouns, verbs, adjectives and phrases
in the collection.
*/
Ext.define('WordSeer.view.metadata.RangeFacets', {
	extend: 'Ext.Container',
	alias: 'widget.rangefacets',
	requires: ['WordSeer.view.metadata.facet.RangeFacet'],
	config: {
		/**
		@cfg {WordSeer.store.MetadataTreeStore} store The store holding the
		metadata for this overview.
		*/
		store: null
	},
	layout: {
		type: 'vbox',
		align: 'stretch'
	},
	constructor: function(cfg) {
		this.initConfig(cfg);
		cfg.autoEl = {
			tag: 'div',
			cls: 'rangefacets',
			children: [
				{
					tag: 'div',
					cls: 'overview-render-target',
					children: []
				}
			]
		};
		this.initConfig(cfg);
		this.callParent(arguments);
	},
	initComponent: function() {
	    var layout = this.getLayout();
	    var me = this;
	    layout.getRenderTarget = function() {
	        var target = this.owner.el.down('div.overview-render-target');
	        this.innerCt = target;
	        this.outerCt = target;
	        return target;
	    };
	    me.addListener('afterrender', function(me) {
	        me.populate();
	    });
	    me.store.addListener('load', function() {
	    	me.populate();
	    })
	    me.callParent(arguments);
	},

	populate: function() {
	    var me = this;
	  	Ext.suspendLayouts();
	    me.removeAll();
		var root = this.getStore().getRootNode();
		if (root) {
			var children = root.childNodes;
			if (children) {
				children.forEach(function(child) {
					if (child.get('type') != 'string') {
						me.add({
							xtype: 'rangefacet',
							title: child.get('displayName'),
							info: child,
							itemId: child.get('propertyName'),
							collapsible: true,
							listeners: {
								afterrender: function(view) {view.draw();}
							}
						});
					}
				});
			}
		}
		Ext.resumeLayouts(true);
	}
});
