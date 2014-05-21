/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.collections.words.PhraseSetList',{
    extend:'WordSeer.view.collections.subsets.SubsetsList',
    alias:'widget.phrasesetlist',
    requires:[
        'WordSeer.store.PhraseSetStore',
    ],
    store: 'PhraseSetStore',
    columns:[
        {
            xtype:'treecolumn',
            text:'Name',
            dataIndex:'text',
            sortable:true,
            flex:3,
            editor:{xtype:'textfield', allowBlank:'false'},
            renderer: function(text, metaData, record) {
                return WordSeer.model.SubsetModel
                    .makeSubsetTag(record.get('id'), text);
            }
        },
        {
            text:'Items',
            dataIndex:'words',
            sortable:true,
            flex:1,
            renderer: function(words) {
                if (words.trim().length > 0){
                    return words.trim().split(" ").length
                } else {
                    return 0;
                }
            }
        }
    ],
    listeners: {
        afterrender: function( eOpts ) {
            view = this.getView();
            view.tip = Ext.create('Ext.tip.ToolTip', {
                target: view.el,
                delegate: view.itemSelector,
                trackMouse: true,
                renderTo: Ext.getBody(),
                listeners: {
                    beforeshow: function updateTipBody(tip) {
                        tip.update(
                            "Right click to rename, double click to open.");
                    }
                }
            });
        }
    }
})
