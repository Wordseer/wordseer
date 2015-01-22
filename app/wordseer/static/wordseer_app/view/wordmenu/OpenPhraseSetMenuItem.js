/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A {@link WordSeer.view.wordmenu.WordMenu word menu} item to open a
{@link WordSeer.model.PhraseSetModel}.
*/
Ext.define("WordSeer.view.wordmenu.OpenPhraseSetMenuItem", {
	extend: "WordSeer.view.menu.MenuItem",
	alias:'widget.openphrasesetmenuitem',
	action: 'open-phrase-set',
	config: {
		/**
		@cfg {Boolean} createNew Whether or not to create a new, emtpy word set
		when this option is clicked. Default: `false`.
		*/
		createNew: false,

		/**
		@cfg {WordSeer.model.PhraseSetModel} PhraseSet The word set to open.
		*/
		PhraseSet: false,
	},
	initComponent: function() {
		if (this.getPhraseSet()) {
			var words = this.getPhraseSet().get('words').trim();
			phrase_set_length = words.length === 0? 0 : words.split(' ').length;
			this.setText(this.getPhraseSet().get('text') + ' (' +
				phrase_set_length + ')');
			if (phrase_set_length > 0) {
				this.setMenu([{
					plain: 'true',
					text: words.replace(" ", ", "),
				}]);
			}
			this.setIconCls('phrase-sets-window');
		} else if (this.getCreateNew()) {
			this.setText('New...');
			this.setIconCls('new-set');
		}
	}
});
