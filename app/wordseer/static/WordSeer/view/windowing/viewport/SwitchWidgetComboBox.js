/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A combobox that allows the user to switch the
{@link WordSeer.view.widget.Widget} displaying the search
results between the following:
	- {@link WordSeer.view.widget.WordTreeWidget}
	- {@link WordSeer.view.widget.ColumnVisWidget}
	- {@link WordSeer.view.widget.SearchWidget}
	- {@link WordSeer.view.widget.DocumentBrowserWidget}
*/
Ext.define('WordSeer.view.windowing.viewport.SwitchWidgetComboBox', {
	extend: 'Ext.form.field.ComboBox',
	alias: 'widget.switch-widget-combobox',
	queryMode: 'local',
    displayField: 'name',
    name: 'widget_xtype',
    editable: false,
    valueField: 'widget_xtype',
    value: 'sentence-list-widget',
    initComponent: function() {
    	this.store = Ext.create('Ext.data.Store', {
    		fields: ['widget_xtype', 'name'],
    		data: [
    			{
    				widget_xtype: 'word-tree-widget',
    				name: 'Word Tree',
    			},
                {
                    widget_xtype: 'word-frequencies-widget',
                    name: 'Word Frequencies',
                },
    			{
    				widget_xtype: 'search-widget',
    				name: 'Grammatical relations',
    			},
                {
                    widget_xtype: 'sentence-list-widget',
                    name: 'Sentences',
                },
    			{
    				widget_xtype: 'document-browser-widget',
    				name: 'Documents',
    			},
                {
                    widget_xtype: 'document-viewer-widget',
                    name: 'Reader'
                },
    			// {
    			// 	widget_xtype: 'column-vis-widget',
    			// 	name: 'Column Visualization',
    			// }
    		]
    	});
    	this.callParent(arguments);
    }

});
