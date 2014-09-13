/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Holds the list of words of a given part of speech that most frequently
appear in sentences matching the main search. This view gets displayed in the
{@link WordSeer.view.widget.Widget} along with the list of frequent phrases.
*/
Ext.define('WordSeer.view.frequentwords.FrequentWordsList', {
	extend: 'WordSeer.view.table.Table',
	alias: 'widget.frequent-words',
	requires: [
		'WordSeer.store.FrequentWordsStore'
	],
	config: {
		/**
		@cfg {String} pos The part of speech of the words in this list.

		*/
		pos: 'N',

		/**
		@cfg {Boolean} groupedByStem Whether or not the words in this list are
		grouped by stem.
		*/
		groupedByStem: true,

		/**
		@cfg {Boolean} orderedByDiffProp Whether or not the words in this list are
		ordered by difference of proportion (i.e. distinctiveness)
		*/
		orderedByDiffProp: true
	},
	selectable: false,
	width: "100%",
	options: [
		{
			label: 'Group by stem?',
			option: {
				tag: 'span',
				cls: 'checkbox checked',
				action: 'group-by-stem',
			},
			listeners: [
				{
					event: 'click',
				}
			]
		},
	],
	columns: [
		{
			field: 'word',
			headerTitle: 'Word',
			headerCls: 'frequent-word-word',
			renderer: function(record, field){
				var word = record.get(field);
				html = "<span class='word'>"+word+"</span> ";
				var sets = record.get('phrase_set');
				if (sets.trim().length  > 0) {
					var ids = sets.trim().split(" ");
					for (var j = 0; j < ids.length; j++) {
						html += WordSeer.model.
							SubsetModel.makeSubsetTag(ids[j]);
					}
				}
				return {tag: 'td', cls:'frequent-word-word', html: html};
			}
		},
		{
			field: 'count',
			headerCls: 'frequent-word-count',
			headerTitle: 'Sents',
			renderer: function(record, field) {
				var count = record.get(field);
				return {tag: 'td', cls:'frequent-word-count', html:count};
			}
		},
		{
			field: 'document_count',
			headerCls: 'frequent-word-count',
			headerTitle: 'Docs',
			renderer: function(record, field) {
				var count = record.get(field);
				return {tag: 'td', cls:'frequent-word-count', html:count};
			}
		},
		{
			field: 'score_sentences',
			headerCls: 'frequent-word-count',
			headerTitle: 'Distinctiveness',
			renderer: function(record, field) {
				var count = record.get(field);
				var svg = '<svg class="lollipop" data-score="'+ (1 - 1 / count)
					+'"></svg>';
				return {tag: 'td', cls:'frequent-word-count distinct', html:count};
			},
			sortDirection: "DESC"
		}
	],
	// title: 'Frequent Words',
	constructor: function(cfg) {
		if (cfg.pos == 'N') {
			// cfg.title = 'Nouns';
		} else if (cfg.pos == 'V') {
			// cfg.title = 'Verbs';
		} else if (cfg.pos == 'J') {
			// cfg.title = 'Adjectives';
		}
		this.callParent(arguments);
		this.autoEl.cls += ' frequent-words-list';
	},
	initComponent: function() {
		this.addEvents('search');
		if (!this.store) {
			this.store = Ext.create('WordSeer.store.FrequentWordsStore', {
				pos: this.getPos()
			});
		}
		this.callParent(arguments);
	},
});
