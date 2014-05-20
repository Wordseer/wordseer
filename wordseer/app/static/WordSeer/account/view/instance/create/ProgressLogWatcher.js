/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('Account.view.instance.create.ProgressLogWatcher', {
	extend: 'Ext.window.Window',
	alias: 'widget.progresslogwatcher',
	modal: false,
	width: 600,
	height:500,
	layout: 'fit',
	statics: {
		url: '../python/instance_processing.py',
	},
	config: {
		instanceId: false,
	},
	bbar: [
		{
			text: 'Stop processing',
			action:'stop_processing',
		},
		{
			text: 'Start processing',
			action: 'start_processing',
			disabled:true,
		},
	],
	items: [
		{html:''}
	]
})