/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A list of frequent phrases with checkboxes for filtering by stop words and
lemmatization.
*/
Ext.define('WordSeer.view.phrases.PhrasesList', {
	alias: 'widget.phraseslist',
	extend: 'WordSeer.view.frequentwords.FrequentWordsList',
	requires: [
		'WordSeer.store.PhrasesStore',
	],
	title: 'Phrases',
	has_function_words: false,
	length: 2,
	width: 300,
	height: 250,
	options: [
		{

			label: 'Stop words',
			option: {
				tag: 'span',
				cls: 'checkbox',
				name: 'has_function_words',
			},
			listeners: [{event: 'click'}],
		},
		{
			label: 'length',
			option: {
				tag:'select',
				name: 'length',
				children: [
					{tag: 'option', value: 2, selected: 'selected', html: 2},
					{tag: 'option', value: 3, html: 3},
					{tag: 'option', value: 4, html: 4},
				]
			},
			listeners: [{event: 'change'}],
		},
		{
			label: 'Distinctive first',
			option: {
				tag: 'span',
				cls: 'checkbox checked',
				action: 'order-by-diffprop',
			},
			listeners: [
				{
					event: 'click',
				}
			]
		}
	],
	columns: [
		{
			headerTitle: 'Phrase',
			field: 'sequence',
			headerCls: 'frequent-word-word',
			renderer: function(record, field) {
				return {
					tag: 'td',
					cls: 'frequent-word-word',
					html: record.get(field)
				};
			}
		},
		{
			headerTitle: 'Sents',
			field: 'count',
			headerCls: 'frequent-word-count',
			renderer: function(record, field) {
				return {
					tag: 'td',
					cls: 'frequent-word-count',
					html: record.get(field)
				};
			}
		},
		{
			headerTitle: 'Docs',
			field: 'document_count',
			headerCls: 'frequent-word-count',
			renderer: function(record, field) {
				return {
					tag: 'td',
					cls: 'frequent-word-count',
					html: record.get(field)+''
				};
			}
		}
	],
	initComponent: function() {
		if (!this.store) {
			this.store = Ext.create('WordSeer.store.PhrasesStore');
		}
		this.addEvents('search');
		this.callParent(arguments);
	},
});
