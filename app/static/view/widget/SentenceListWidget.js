/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.widget.SentenceListWidget',{
    extend:'WordSeer.view.widget.Widget',
    requires:[
        'WordSeer.view.sentence.SentenceList'
    ],
    alias:'widget.sentence-list-widget',
    items:[
        {
            xtype:'sentence-list',
            height: 450,
            width: '95%',
            itemID:'sentence-list',
        },
    ],
});
