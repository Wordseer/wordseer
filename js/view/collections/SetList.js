Ext.define('WordSeer.view.collections.SetList', {
	extend: 'WordSeer.view.treepanel.Treepanel',
	alias: 'widget.sets-list',
	config: {
		/**
		@cfg {String} type The type of the collection.
		*/
		type: '',

		/**
		@cfg {WordSeer.store.MetadataTreeStore} metadataStore The metadata store
		that matches the layout panel for which the set list is being used as a
		filter
		*/
		metadataStore: null
	},
	collapsible: true,
	selectable: false,
	constructor: function(cfg) {
		this.callParent(arguments);
		this.autoEl.cls += ' sets-list';
	},
	options: [
		{
			option: {
				tag: 'span',
				html: 'New Set',
				cls: 'button',
				action: 'new-set'
			},
			listeners: [
				{
					event: 'click'
				},
				{
					event: 'mouseleave'
				}
			],
		}
	],
	columns: [
		{
			field: 'text',
			headerTitle: 'Set',
			headerCls: 'frequent-word-word',
			renderer: function(record, field, view) {
				return {
					tag: 'td',
					html: record.get(field),
					cls: 'frequent-word-word',
				};
			}
		},
		{
			field: 'sentence_count',
			headerTitle: 'Sentences',
			headerCls: 'frequent-word-count',
			renderer: function(record, field, view) {
				var matched_sentence_count = view.getMatchedCount(
					record, 'count');
				return {
					tag: 'td',
					html: matched_sentence_count + "/" + record.get(field),
					cls: 'frequent-word-count',
				};
			}
		},
		{
			field: 'document_count',
			headerTitle: 'Documents',
			headerCls: 'frequent-word-count',
			renderer: function(record, field, view) {
				var matched_document_count = view.getMatchedCount(
					record, 'document_count');
				return {
					tag: 'td',
					html: matched_document_count + "/" + record.get(field),
					cls: 'frequent-word-count',
				};
			}
		}
	],

	getMatchedCount: function(record, property) {
		var me = this;
		var id = record.get('id') + "";
		var count = 0;
		me.getMetadataStore().getRootNode().cascadeBy(function(node){
			if (node.get('propertyName') == (me.getType() + "_set") &&
				node.get('value') == id) {
				count = node.get(property);
			}
		});
		return count;
	}
});
