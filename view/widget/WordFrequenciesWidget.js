/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.view.widget.WordFrequenciesWidget', {
	extend:'WordSeer.view.widget.Widget',
	requires:[
		'WordSeer.view.visualize.wordfrequencies.WordFrequencies',
	],
	alias: 'widget.word-frequencies-widget',
	items:[
		{xtype:'word-frequencies', height: 800},
	]
});

