/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Displays a drop-down menu of the metadata values and counts that
match the current search query. Backed by a
{@link WordSeer.store.MetadataListStore} instance, used by the
{@link WordSeer.view.metadata.facet.StringFacets} view as an autosuggest form.
*/
Ext.define("WordSeer.view.metadata.MetadataComboBox", {
	extend: 'Ext.form.field.ComboBox',
	alias: 'widget.metadata-combobox',
	requires: [
		'WordSeer.store.MetadataListStore',
	],
	config: {
		oldQueryString: ""
	},
	initComponent: function() {
		this.store = Ext.create('WordSeer.store.MetadataListStore');
		this.callParent(arguments);
	},
	queryMode: 'local',
	valueField: 'text',
	enableKeyEvents: true,
	queryDelay: 500,
	emptyText: 'Start typing',
	autoSelect: true,
	forceSelection: true,
	disableKeyFilter:true,
	value: "",
	displayField: 'text',
	listConfig: {
		getInnerTpl: function() {
			var template ='<span class="combo-box-metadata">';
            template += '{propertyName}: {text} ({count})';
            template += '</span>';
            return template;
		}
	},
})
