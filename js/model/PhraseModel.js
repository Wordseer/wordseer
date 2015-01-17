/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Represents a phrase. Used by the {@link WordSeer.view.phrases.PhrasesList}
as the model backing the {@link WordSeer.store.PhrasesStore}.
*/
Ext.define('WordSeer.model.PhraseModel', {
	extend: 'Ext.data.Model',
	fields: [
		/**
		@cfg {String} id The id of the phrase.
		*/
		{type: 'string', name: 'id'},

		/**
		@cfg {String} sequence The text of the phrase itself.
		*/
		{type: 'string', name: 'sequence'},

		/**
		@cfg {String} class What type of object this is -- a phrase. Used when
		the {@link WordSeer.model.FormValues} is trying to decide how to
		serialize this to send to the server when it's passed in as a filter
		parameter, and by the {@link WordSeer.view.wordmenu.WordMenu} when
		displaying a context menu.
		*/
		{type: 'string', name: 'class', defaultValue:'phrase'},

		/**
		@cfg {Integer} count The number of times this phrase occurs in a
		particular context.
		*/
		{type: 'int', name: 'count'},

		/**
		@cfg {Integer} document_count The number of documents in which this
		phrase occurs.
		*/
		{type: 'int', name: 'document_count'},

		/**
		@cfg {Integer} sentence_count The number of sentences in which this
		phrase occurs.
		*/
		{type: 'int', name: 'sentence_count'},

		/**
		@cfg {Integer} has_function_words Whether (1) or not (0) this phrase
		contains stop words.
		*/
		{type: 'int', name: 'has_function_words'},

		/**
		@cfg {Integer} all_function_words Whether (1) or not (0) this phrase
		only contains function words.
		*/
		{type: 'int', name: 'all_function_words'},

		/**
		@cfg {Integer} lemmatized Whether (1) or not (0) this phrase is
		lemmatized.
		*/
		{type: 'int', name: 'lemmatized'},

		/**
		@cfg {Integer} length The length of this sequence
		*/
		{type: 'int', name: 'length'},

		/**
		@cfg {Float} diffprop_sentences The difference of proportions of this
		phrase in this slice, computed by calculating sentence proportion.
		*/
		{name: 'diffprop_sentences', type: 'float', defaultValue: 0.0},

		/**
		@cfg {Float} diffprop_documents The difference of proportions of this
		phrase in this slice, computed by calculating document proportion.
		*/
		{name: 'diffprop_documents', type: 'float', defaultValue: 0.0},

	]
});
