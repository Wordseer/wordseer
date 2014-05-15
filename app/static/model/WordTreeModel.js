/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Represents a word tree node. Used by the view
{@link WordSeer.view.visualize.wordtree.WordTree}.
*/
Ext.define('WordSeer.model.WordTreeModel', {
	extend: 'Ext.data.Model',
	fields: [
		{name:'isRoot', type: 'boolean', default: false},
		{name: 'count', type: 'int', default: 1},
		{name: 'key', type: 'string', default:''},
		{name: 'all_children', type: 'auto', default: []},
		{name: 'children', type: 'auto', default: []},
		{name: 'hidden_children', type: 'auto', default: []},
	],
});
