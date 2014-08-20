/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code.
*/Ext.define('WordSeer.view.widget.SentenceTableWidget',{
    extend:'WordSeer.view.widget.Widget',
    requires:[
        'WordSeer.view.sentence.SentenceTable'
    ],
    alias:'widget.sentence-table-widget',
    items:[
        {
            xtype:'sentence-table',
            height: 450,
            width: '95%',
            itemID:'sentence-list',
        },
    ],
});
