/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.columnvis.ColumnVisWidget',{
    extend:'WordSeer.view.widget.Widget',
    requires:[
        'WordSeer.view.visualize.columnvis.ColumnVis'
    ],
    title:'Column Visualization',
    alias:'widget.column-vis-widget',
    layout:'fit',
    items:[
        {xtype:'column-vis'},
    ],
})