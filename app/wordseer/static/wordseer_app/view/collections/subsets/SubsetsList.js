/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
WordSeer.collections.subsets.SubsetsList

A general treepanel class for displaying subsets

Inheritor classes:
    - WordSeer.view.collections.DocumentSetList
    - WordSeer.view.collections.DocumentSetList
    - WordSeer.collections.words.PhraseSetList
**/
Ext.define('WordSeer.view.collections.subsets.SubsetsList',{
    extend:'Ext.tree.Panel',
    alias:'widget.subsetslist',
    requires:[
        'WordSeer.view.collections.subsets.SubsetsBBar',
    ],
    bbar:{
        xtype:'subsets-toolbar'
    },
    layout: 'fit',
    autoScroll:true,
    useArrows:true,
    rootVisible:false,
    plugins:[
     {
       ptype:'cellediting',
       clicksToEdit: 0,
    }
    ],
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
            dataIndex:'ids',
            sortable:true,
            flex:1,
            renderer: function(ids) {
                return ids.length
            }
        }
    ],
    initComponent:function(){
        this.addEvents('searchParamsChanged');
        this.enableBubble('searchParamsChanged');
        this.addEvents('addedSet', 'deletedSet', 'subsetschanged');
        this.callParent(arguments);
        this.getStore().load();
    },
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
                            "Right click to rename. Click to open");
                    }
                }
            });
        }
    }

})
