/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.windowing.overview.Overview', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.overview',
	id: 'overview',
	requires: [
		'WordSeer.view.windowing.overview.LayoutPicker',
		'WordSeer.view.windowing.overview.LayoutThumbnail',
		'WordSeer.view.windowing.overview.WindowThumbnail',
	],
	items: [
		{html: 'overview'}
	],
	layout: 'fit',
	tbar: {
		layout: 'hbox',
		items: [
			{
				xtype: 'button',
				action: 'switch-to-viewport',
				text: 'Close overview',
			},
			'-',
			{xtype: 'layoutpicker'}
		]
	},
	hidden: true,

})