/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
A text field that shows auto-suggest suggestions beneath it as the user types
*/
Ext.define('WordSeer.view.autosuggest.AutoSuggestTextField', {
	extend: 'Ext.form.field.Text',
	alias: 'widget.autosuggest-textfield',
	requires: [
		'WordSeer.view.autosuggest.AutoSuggestMenu'
	],
	config: {
		/** @cfg {Object/WordSeer.view.autosuggest.AutoSuggestMenu} menu The
		autoSuggest menu (or config).
		*/
		menu: null,

		/** @cfg {Ext.data.Model} record The selected item.
		*/
		record: null
	},

	initComponent: function() {
		this.menu = Ext.widget(this.menu.xtype, this.menu);
		this.menu.textfield = this;
		this.menu.floatParent = this;
		this.addListener('change', this.valueChanged);
		this.addListener('specialkey', this.specialkey);
	},

	valueChanged: function(view, newValue, oldValue) {
		if (view.hasFocus) {
			if (newValue != oldValue) {
				var search_lemmas = view.up().down("checkbox[name=all_word_forms]").value;
				view.menu.hide();
				view.menu.refresh(newValue, search_lemmas);
			}
		}
	},

	specialkey: function(view, event) {
		if (event.getKey() == event.DOWN) {
			var first_menu_item = this.menu.query('autosuggest-menuitem:first')[0];
			first_menu_item.highlight();
		} else if (event.getKey() == event.ENTER) {
			this.menu.hide();
		}
	},

	keypress: function(view, event) {
		special = [event.ENTER, event.UP, event.DOWN, event.LEFT, event.RIGHT];
		if (special.indexOf(event.getKey()) == -1) {
			view.record = null;
		}
	}
});
