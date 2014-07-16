/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A {@link WordSeer.view.wordmenu.WordMenu word menu} item to display an
auto-suggest suggestion.
*/
Ext.define("WordSeer.view.autosuggest.AutoSuggestMenuItem", {
	extend: "WordSeer.view.menu.MenuItem",
	alias:'widget.autosuggest-menuitem',
	config: {

		/**
		@cfg {Ext.data.Model} record The record holding the data being displayed.
		*/
		record: false,

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

	},
	constructor: function(cfg) {
		this.initConfig(cfg);
		if (this.record) {
			this.text = (this.record.get(this.textField) + ' (' +
				this.record.get(this.countField) + ')');
		}
		this.callParent(arguments);
		this.autoEl.cls += ' autosuggest-menuitem';
	},

	populate: function() {
		var me = this;
		me.getEl().on('click', function(event) {
			var textfield = me.up('autosuggest-menu').textfield;
			textfield.setValue(me.record.get(
				me.textField));
			textfield.setRecord(me.record);
			textfield.focus();
			textfield.fireEvent('change', textfield);
		});
		me.getEl().on('keydown', function(event) {
			if (event.getKey() == event.ENTER) {
				var textfield = me.up('autosuggest-menu').textfield;
				textfield.setValue(me.record.get(
					me.textField));
				textfield.setRecord(me.record);
				textfield.focus();
				textfield.fireEvent('change', textfield);
				me.up().close(10);
			}
		});
		me.callParent(arguments);
	}
});
