/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.ColumnVisModule',{
    extend:'WordSeer.view.desktop.Module',
    requires:[
        'WordSeer.view.visualize.columnvis.ColumnVisWidget',
      ],
    id:'strip-vis',
    inputClass:['word', 'grammatical', 'phrase-set'],
    text:'Column Visualization',
    widgetClass:'WordSeer.view.visualize.columnvis.ColumnVisWidget',
});
