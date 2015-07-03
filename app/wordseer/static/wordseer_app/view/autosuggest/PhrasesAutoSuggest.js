/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
A text field that shows auto-suggest suggestions beneath it as the user types
in a search query
*/
Ext.define('WordSeer.view.autosuggest.PhrasesAutoSuggest', {
	extend: 'WordSeer.view.autosuggest.AutoSuggestTextField',
	requires: [
		'WordSeer.store.PhrasesAutoSuggestStore'
	],
	alias: 'widget.phrases-autosuggest',
	config: {
		cls: 'x-table-plain'
	},
	initComponent: function() {
		this.menu = {
			xtype: 'autosuggest-menu',
			menuItemXtype: 'phrases-autosuggest-menuitem',
			floatParent: this,
			store: Ext.create('WordSeer.store.PhrasesAutoSuggestStore'),
			textField: 'text',
			countField: 'sentence_count',
		};
		this.callParent(arguments);
	},

	setValue: function(value) {
		if ($.isNumeric(value)) {
			var record = Ext.getStore('PhraseSetListStore').getById(
				parseInt(value));
			this.value = record.get('text');
		} else {
			this.value = value;
		}
		this.callParent([this.value]);
	},


	getSubmitValue: function() {
		if (!this.record || this.record.get('text') != this.getValue()) {
			this.record = null;
			return this.getValue();
		} else if (this.record) {
			cls = this.record.get('class');
			if (cls === 'phrase') {
				return this.record.get('text');
			} else if (cls == 'phrase_set') {
				return this.record.get('id');
			} else if (cls == 'metadata') {
				return ''
			}
		} else {
			return this.getValue();
		}
	},
});
