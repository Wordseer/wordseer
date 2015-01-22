/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A {@link WordSeer.view.wordmenu.WordMenu word menu} item to open a
{@link WordSeer.model.PhraseSetModel}.
*/
Ext.define("WordSeer.view.wordmenu.OpenSentenceSetMenuItem", {
	extend: "Ext.menu.Item",
	alias:'widget.open-sentence-set-item',
	action: 'open-sentence-set',
	config: {
		/**
		@cfg {Boolean} createNew Whether or not to create a new, emtpy word set
		when this option is clicked. Default: `false`.
		*/
		createNew: false,

		/**
		@cfg {WordSeer.model.SubsetModel} record
		The set to open.
		*/
		record: false,

		/**
		@cfg {String} sentenceId The sentence ID of the sentence that was
		clicked to produce this menu.
		*/
		sentenceId: '',
	},
	initComponent: function() {
		if (this.getRecord()) {
			this.setText(this.getRecord().get('text') + ' ('
				+ this.getRecord().get('ids').length + ')');

		} else if (this.getCreateNew()) {
			this.setText('New...');
			this.setIconCls('new-set');
		}
	}
})
