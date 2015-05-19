/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Holds the list of words of a given part of speech that most frequently
appear in sentences matching the main search. This view gets displayed in the
{@link WordSeer.view.widget.Widget} along with the list of frequent phrases.
*/
Ext.define('WordSeer.view.frequentwords.FrequentWordsList', {
	extend: 'WordSeer.view.table.Table',
	alias: 'widget.frequent-words',
	requires: [
		'WordSeer.store.AssociatedWordsStore'
	],
	config: {
		/**
		@cfg {Boolean} groupedByStem Whether or not the words in this list are
		grouped by stem.
		*/
		groupedByStem: true,
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
				// var sets = record.get('phrase_set');
				// if (sets && sets.trim().length  > 0) {
				// 	var ids = sets.trim().split(" ");
				// 	for (var j = 0; j < ids.length; j++) {
				// 		html += WordSeer.model.
				// 			SubsetModel.makeSubsetTag(ids[j]);
				// 	}
				// }
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
			field: 'doc_count',
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
				var svg = '<svg class="lollipop" data-score_sentences="'+ count
					+'"></svg>';
				return {tag: 'td', cls:'frequent-word-count distinct', html:svg};
			},
			sortDirection: "DESC"
		}
	],
	// title: 'Frequent Words',
	constructor: function(cfg) {
		this.callParent(arguments);
		this.autoEl.cls += ' frequent-words-list';
		// filter the store by POS
		// suspent events to avoid triggering a premature 'datachanged' action
		this.store.suspendEvents(); 
		this.store.filter("category", cfg.pos);
		this.store.resumeEvents();
	},
	initComponent: function() {
		this.addEvents('search');
		this.callParent(arguments);
	},
});
