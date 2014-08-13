/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A widget for adding an item to a {@link WordSeer.model.PhraseSet}
*/
Ext.define('WordSeer.view.widget.PhraseSetsWidget', {
	extend: 'WordSeer.view.widget.Widget',
	alias: 'widget.phrase-sets-widget',
	items: [{xtype:'phrase-sets'}],
	dockedItems:[],
	layout:'fit',
	title: 'Word Sets',
});
