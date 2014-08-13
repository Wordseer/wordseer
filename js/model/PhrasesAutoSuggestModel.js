/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Represents a phrase. Used by the {@link WordSeer.view.phrases.PhrasesList}
as the model backing the {@link WordSeer.store.PhrasesStore}.
*/
Ext.define('WordSeer.model.PhrasesAutoSuggestModel', {
	extend: 'Ext.data.Model',
	fields: [
		/**
		@cfg {String} id The id of the phrase.
		*/
		{type: 'string', name: 'id'},

		/**
		@cfg {String} text The text of the item itself.
		*/
		{type: 'string', name: 'text'},

		/**
		@cfg {String} text In case of metadata autosuggest, the property name
		of the item.
		*/
		{type: 'string', name: 'property_name', defaultValue: ''},

		/**
		@cfg {String} text In case of metadata autosuggest, the value
		of the item.
		*/
		{type: 'string', name: 'value', defaultValue: ''},

		/**
		@cfg {String} class What type of object this is -- a phrase. Used when
		the {@link WordSeer.model.FormValues} is trying to decide how to
		serialize this to send to the server when it's passed in as a filter
		parameter, and by the {@link WordSeer.view.wordmenu.WordMenu} when
		displaying a context menu.
		*/
		{type: 'string', name: 'class', defaultValue:'phrase'},

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
		@cfg {Integer} length The length of the sequence (if class = 'phrase')
		in which this.
		*/
		{type: 'int', name: 'length', defaultValue: 0},

	]
});
