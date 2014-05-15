/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.windowing.overview.WindowThumbnail', {
	extend: 'Ext.panel.Panel',
	requires: 'WordSeer.model.HistoryItemModel',
	alias: 'widget.windowthumbnail',
	html: 'thumbnail',
	configs: {
		windowModel: false,  // A HistoryItemModel instance.
		belongsTo: false,
		isSelected: false,
	}
})