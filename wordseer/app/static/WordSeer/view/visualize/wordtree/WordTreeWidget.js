/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.wordtree.WordTreeWidget',{
    extend:'WordSeer.view.widget.Widget',
    requires:[
        'WordSeer.view.visualize.wordtree.WordTree'
    ],
    alias:'widget.word-tree-widget',
    width:700,
    items:[
        {xtype:'word-tree', itemID:'word-tree'},
    ],
});
