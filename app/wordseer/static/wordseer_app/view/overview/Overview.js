/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Displays an overview of the most frequent nouns, verbs, adjectives and phrases
in the collection.
*/
Ext.define('WordSeer.view.overview.Overview', {
	extend: 'Ext.Container',
	alias: 'widget.overview',
	requires: ['WordSeer.view.overview.TagListOverview'],
	config: {
		/**
		@cfg {WordSeer.model.LayoutPanelModel} model The LayoutPanelModel
		holding all the stores for the overview.
		*/
		model: Ext.create('WordSeer.model.LayoutPanelModel'),

		/**
		@cfg {String} title The title of this overview.
		*/
		title: '',

		/**
		@cfg {String} iconCls The icon for this overview.
		*/
		iconCls: ''
	},
	layout: {
		type: 'vbox',
		align: 'stretch'
	},
	width: 400,
	constructor: function(cfg) {
		this.initConfig(cfg);
		cfg.autoEl = {
			tag: 'div',
			cls: 'overview',
			children: [
				{
					tag: 'div',
					cls: 'overview-header',
					children: [
						{
							tag: 'span',
							cls: 'overview-header-icon ' + this.iconCls,
						},
						{
							tag: 'h1',
							html: this.title
						}
					]
				},
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
	    layout.getRenderTarget = function() {
	        var target = this.owner.el.down('div.overview-render-target');
	        this.innerCt = target;
	        this.outerCt = target;
	        return target;
	    };
	    this.callParent(arguments);
	    this.addListener('afterrender', function(me) {
	        me.populate();
	    });
	},
	populate: function() {
	    var me = this;
	}
});
