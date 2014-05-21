Ext.define('WordSeer.view.metadata.facet.StringFacets', {
	extend: 'WordSeer.view.treepanel.MultiTable',
    alias: 'widget.stringfacets',
    rootVisible: false,
    config: {
    	filterFn: function(record) {
    		return record.get('type')  == "string";
    	}
    },
    constructor: function(cfg) {
    	Ext.apply(this, cfg);
    	this.initConfig(cfg);
    	this.callParent(arguments);
    },
    columns: [
        {
            field: 'text',
            headerTitle: 'Category',
            headerCls: 'metadata-value',
            renderer: function(record, field) {
                return {
                    tag: 'span',
                    html: record.get(field),
                    cls: 'metadata-value',
                };
            }
        },
        {
            field: 'count',
            headerTitle: 'Sentences',
            headerCls: 'metadata-count',
            renderer: function(record, field) {
                return {
                    tag: 'span',
                    html: record.get(field),
                    cls: 'metadata-count',
                };
            }
        },
        {
            field: 'document_count',
            headerTitle: 'Documents',
            headerCls: 'metadata-count',
            renderer: function(record, field) {
                return {
                    tag: 'span',
                    html: record.get(field),
                    cls: 'metadata-count',
                };
            }
        }
    ]
});
