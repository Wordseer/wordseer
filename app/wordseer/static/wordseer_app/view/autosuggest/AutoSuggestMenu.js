/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
A menu that appears under a textfield with auto-suggest suggestions and
supports keyboard events.
*/
Ext.define('WordSeer.view.autosuggest.AutoSuggestMenu', {
	extend: 'WordSeer.view.menu.Menu',
	alias: 'widget.autosuggest-menu',
	requires: [
		'WordSeer.view.autosuggest.AutoSuggestMenuItem',
	],
	width: 300,
	height: 300,
	destroyOnClose: false,
	config: {
		/**
		@cfg {Ext.data.Store} store The store that retrieves autosuggest
		suggestions.
		*/
		store: null,

		/**
		@cfg {String} menuItemXtype The xtype of the autosuggest menuitem.

		*/
		menuItemXtype: 'autosuggest-menuitem',

		/**
		@cfg {String} textField The field within the {@link Ext.data.Model}
		stored by the {@link #store} that supplies the text for the display.

		*/
		textField: 'text',

		/**
		@cfg {String} countField The field within the {@link Ext.data.Model}
		stored by the {@link #store} that supplies the count for the display.

		*/
		countField: 'count',

		/**
		@cfg {Ext.Component} textfield The parent under which to show this menu.
		*/
		textfield: null

	},

	autoEl: {
		tag: 'ul',
		cls: 'autosuggest-menu'
	},
	constructor: function(cfg) {
		this.initConfig(cfg);
		this.callParent(arguments);
	},

	refresh: function(query, search_lemmas) {
		var me = this;
		me.removeAll();
		me.getStore().load({
			scope: me,
			params: {
				query: query,
				search_lemmas: search_lemmas
			},
			callback: function(records, operation, success) {
					var items = [];
					records.forEach(function(record, i) {
						items.push({
							xtype: me.menuItemXtype,
							record: record,
							textField: me.textField,
							countField: me.countField
						});
					});
					this.add(items);
					if (items.length > 0) {
						this.showBy(this.textfield, 'tl-bl?');
						this.textfield.focus();
					}
				}
		});
	},
});
