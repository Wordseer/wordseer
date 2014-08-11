/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.collections.words.PhraseSetsPanel',{
    extend:'WordSeer.view.desktop.panel.Panel',
    alias:'widget.phrase-sets',
    requires:[
        'WordSeer.view.collections.words.PhraseSetCanvas',
        'WordSeer.view.collections.words.PhraseSetList',
    ],
    constrain:true,
    layout: 'border',
    itemID:'phrase-set-panel',
    items:[
        {
            region:'west',
            itemId:'west-panel',
            title:'Word Sets',
            layout:'fit',
            width:190,
            items:[
                {
                    xtype:'PhraseSetlist',
                    itemId:'phrase-set-list'
                }
            ],
            collapsible:true,
            resizable:true
        },
        {
            region:'center',
            xtype:'PhraseSetcanvas',
            itemId:'phrase-set-canvas'
        }
    ],
    statics:{
        instanceCount:0
    },
    initComponent:function(){
     this.self.instanceCount ++;
     this.callParent(arguments);
    },
});
