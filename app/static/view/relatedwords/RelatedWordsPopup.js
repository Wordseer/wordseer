/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Displays a pop-up showing the most frequent nouns verbs and adjectives that
occur near a word or phrase or word set. Accessed through the
{@link WordSeer.view.wordmenu.WordMenu}.
*/
Ext.define('WordSeer.view.relatedwords.RelatedWordsPopup', {
	extend: 'WordSeer.view.box.Overlay',
	alias: 'widget.related-words-popup',
	requires: [
		'WordSeer.view.relatedwords.RelatedWordsList'
	],
	config: {
		/** @cfg {Object} data The associated words. This object contains
		the keys 'Noun', 'Verb', 'Adjective' and 'Adverb'. Each value is
		an array of {id: word: score: } objects, where the score is the number
		of sentences in which that word co-occurs with the {@link #current}
		word. */
		data: {},

		/** @cfg {WordSeer.model.WordModel} current The word or
		{@link WordSeer.model.PhraseModel} for which these related words are
		being shown. */
		current:{},

		/** @cfg {WordSeer.model.FormValues} formValues The search parameters
		that define the context in which the related word search is occurring
		*/
		formValues:{},
	},
	destroyOnClose: true,
	width: 900,
	height: 400,
	draggable: true,
	constrain: true,
	layout: {
		type: 'hbox',
	},
	title: 'Related Words',
	constructor: function(cfg) {
		this.title = "Words that co-occcur with '" +
			cfg.current.get('word')+"' ";
		this.callParent(arguments);
	},
	initComponent: function() {
		var items = [];
		var context = ".";
		var context_html = WordSeer.model.FormValues.toHtml(
			this.getFormValues().serialize(), " ");
		if (context_html.length > 0) {
			context = " in the context: ";
		}
		this.title += context + context_html;
		var parts_of_speech = ['Nouns', 'Verbs', 'Adjectives', 'Phrases'];
		for (var i = 0; i < parts_of_speech.length; i++) {
			var pos = parts_of_speech[i];
			var words = this.getData()[pos];
			items.push({
				xtype: 'related-words-list',
				data: words,
				title: pos,
				hideHeaders: true,
				fileTitle: pos + " " + this.title,
				pos: pos,
				flex: 1,
			});
		}
		this.items = items;
		this.callParent(arguments);
	}
});
