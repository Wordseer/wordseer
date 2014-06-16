/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.widget.SearchWidget', {
    extend:'WordSeer.view.widget.Widget',
    requires:[
        'WordSeer.view.visualize.barchart.BarCharts',
        'WordSeer.view.sentence.SentenceList',
    ],
    alias: 'widget.search-widget',
    layout: {
        type: 'vbox',
        align: 'stretch'
    },
    height: 600,
    defaults: {
        split: true,
        resizable: true,
        collapsible: true,
    },
    items:[
       {xtype:'bar-charts', flex:1},
       {xtype:'sentence-list', flex:1},
    ]
});

