/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.widget.DocumentBrowserWidget',{
    extend:'WordSeer.view.widget.Widget',
    requires:[
        'WordSeer.view.document.DocumentGrid',
    ],
    title:'Search Results',
    alias:'widget.document-browser-widget',
    items:[
        {
            xtype:'document-grid',
            height:450,
        },
    ],
});
