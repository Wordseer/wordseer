/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.history.HistoryList', {
	requires: [
		'WordSeer.store.HistoryItemStore',
		'WordSeer.store.GrammaticalRelationsStore',
	],
	extend: 'WordSeer.view.table.Table',
	layout: 'fit',
	alias: 'widget.history-list',
	id: 'historylist',
	store: 'HistoryItemStore',
	checkboxes: true,
	multiSelect: true,
	initComponent: function() {
		this.columns = [
		{
			headerTitle:'App',
			field: 'widget_xtype',
			renderer: this.renderModule,
		},
		{
			headerTitle: 'Query',
			field: 'formValues',
			renderer: function(record, field) {
				var serialized = record.get(field);
				return {
					tag: 'td',
					html: WordSeer.model.FormValues.toHtml(serialized, "<br>")
				}
			}
		},
		{
			headerTitle: 'Time',
			field: 'creation_timestamp',
			renderer: this.renderDate,
		},
		{
			headerTitle: 'Last Viewed',
			field: 'last_viewed_timestamp',
			hidden: true,
			renderer: this.renderDate,
		}
	],
		this.grammaticalRelationsStore =
			Ext.getStore('GrammaticalRelationsStore');
		this.callParent(arguments);
	},
	renderDate: function(record, field) {
		var date = record.get(field)
		var date = new Date(date)
		return {tag: 'td', html: Ext.Date.format(date, "g:i a M d y")}
	},
	renderModule: function(record, field) {
		var xtype = record.get(field);
		var name = "";
		if (xtype == 'word-tree-widget') {
			name = 'Tree';
		} else if (xtype == 'word-frequencies-widget') {
			name = 'Frequencies';
		} else if (xtype == 'search-widget') {
			name = 'Grammatical Search Bar Charts';
		} else if (xtype == 'column-vis-widget') {
			name = 'Column Vis';
		} else if (xtype == 'sentence-list-widget' || xtype == 'sentence-table-widget' ) {
			name = 'Search Results';
		} else if (xtype == 'document-browser-widget') {
			name = 'Documents';
		} else if (xtype == 'document-viewer-widget') {
			name = 'Reader';
		} else {
			name = xtype;
		}
		return {
			tag: 'td',
			html: name
		}
	},

})
