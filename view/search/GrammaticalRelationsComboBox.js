/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A combo-box that contains one option for each of the 
{@link WordSeer.store.GrammaticalRelationsStore grammatical relations} in
WordSeer. A component of the {@link WordSeer.view.search.GrammaticalSearchForm
grammatical search form}.
**/
Ext.define('WordSeer.view.search.GrammaticalRelationsComboBox', {
	extend: 'Ext.form.field.ComboBox',
	alias: 'widget.grammaticalrelationscombobox',
	requires: [
	'WordSeer.store.GrammaticalRelationsStore'
	],
	forceSelection:true,
    autoSelect:true,
    enableKeyEvents:true,
    typeAhead:true,
    queryMode:'local',
    displayField:'name',
    valueField:'id', 
    emptyText:'Search or pick relationship ...',
    store: Ext.create('WordSeer.store.GrammaticalRelationsStore'),
})