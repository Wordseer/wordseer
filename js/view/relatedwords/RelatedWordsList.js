/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Holds the list of words of a given part of speech that most frequently
appear in sentences matching the main word. This view is used by the
{@link WordSeer.view.relatedwords.RelatedWordsPopup}.
*/
Ext.define('WordSeer.view.relatedwords.RelatedWordsList', {
	extend: 'WordSeer.view.export.ExportableTable',
	alias: 'widget.related-words-list',
	width: 230,
	height: 380,
	config: {
		/**
		@cfg {Array} data The data to be displayed, a list of words and
		their frequencies in the format
		{id: word: score:} where the score is the number of sentences in which
		that word appeared with the main word.
		*/
		data:[],
		pos: '',
	},
	constructor: function(cfg) {
		this.callParent(arguments);
		this.autoEl.cls += ' related-words-list';
	},
	initComponent: function() {
		this.columns = [
		{
			field: 'word',
			headerCls: 'frequent-word-word',
			headerTitle: this.getPos(),
			flex: 3,
			renderer: function(record, field) {
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
				return {tag: 'td', html:html, cls: 'frequent-word-word'};
			}
		},
		{
			field: 'score',
			headerTitle: 'Sentences',
			headerCls: 'frequent-word-count',
			flex: 1,
			renderer: function(record, field) {
				var count = record.get(field);
				return {tag: 'td', cls:'frequent-word-count', html:count};
			}
		}
		];
		this.store = new Ext.data.Store({
			fields: [
				{type:'number', name: 'score'},
				{type:'string', name: 'word'},
				{type:'number', name: 'id'},
				{type: 'string', name:'phrase_set', defaultValue:''},
			],
			data: this.getData()
		});
		this.callParent(arguments);
	},
});
