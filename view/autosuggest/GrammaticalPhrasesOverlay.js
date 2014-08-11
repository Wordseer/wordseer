/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.view.autosuggest.GrammaticalPhrasesOverlay', {
	alias: 'widget.grammatical-phrases-overlay',
	extend: 'WordSeer.view.box.Overlay',
	destroyOnClose: true,
	title: 'Grammatical Context',
	height: 700,
	width: 500,

	config: {
		/**
		@cfg {Object} relations The grammatical relations of this word
		*/
		relations: null,

		/**
		@cfg {WordSeer.view.autosuggest.AutoSuggestMenuItem} shownBy The
		autosuggest menuitem that this overlay is shown by.
		*/
		shownBy: null,

		/**
		@cfg {WordSeer.model.PhrasesAutoSuggestModel} record The record
		representing the word for which these options are being shown.
		*/
		record: null
	},
	layout:{
		type: 'vbox',
		align: 'stretch'
	},

	autoScroll: true,
	reserveScrollbar: true,

	initComponent:function() {
		var items = [];
		for (var i = 0; i < this.relations.length; i++) {
			var relation = this.relations[i];
			var relation_record = Ext.getStore('GrammaticalRelationsStore')
				.getById(relation.relation);
			var relation_data_store = Ext.create('Ext.data.Store', {
				fields: [
					{name: 'relation_id', type: 'int'},
					{name: 'id', type: 'int'},
					{name: 'sentence_count', type: 'int'},
					{name: 'document_count', type: 'int'},
					{name: 'gov_id', type: 'int'},
					{name: 'dep_id', type: 'int'},
					{name: 'gov_index', type: 'int'},
					{name: 'dep_index', type: 'int'},
					{name: 'gov', type: 'string'},
					{name: 'dep', type: 'string'},
					{name: 'relationship', type: 'string'},
					{name: 'sentence_id', type: 'int'},
					{name: 'document_id', type: 'int'},
					{name: 'html', type: 'string'},
					{name: 'word', type: 'string'},
					{name: 'is_gov', type: 'boolean'},
					{name: 'is_dep', type: 'boolean'},
				],
				data: relation.words
			});
			var table = {
				xtype: 'databox-table',
				store: relation_data_store,
				collapsible: true,
				collapsed: false,
				title: relation_record.get('name'),
				columns: [
					{
						field: 'word',
						headerTitle: 'Word',
					},
					{
						field: 'sentence_count',
						headerTitle: 'Sentences',
					},
					{
						field: 'html',
						headerTitle: 'Example',
						renderer: function(record, field) {
							var html = record.get(field);
							var is_gov = record.get('is_gov');
							search_index = record.get('dep_index');
							match_index = record.get('gov_index');
							if (is_gov) {
								search_index = record.get('gov_index');
								match_index = record.get('dep_index');
							}
							var i = 0;
							html = html.replace(/class='word'/g, function(match){
								cls = "word ";
								if (i == match_index) {
									cls += " match";
								}
								if (i == search_index ) {
									cls += " search";
								}
								i ++;
								return "class = '" + cls + "'";
							});
							return {
								tag: 'td',
								html: html
							};
						}
					},
				]
			};
			items.push(table);
		}

		this.items = items;
		this.callParent(arguments);
	}
});
