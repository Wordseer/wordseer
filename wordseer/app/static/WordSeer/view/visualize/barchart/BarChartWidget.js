/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.barchart.BarChartWidget',{
    extend:'WordSeer.view.widget.Widget',
    requires:[
        'WordSeer.view.visualize.barchart.BarCharts'
    ],
    title:'Bar Chart',
    alias:'widget.bar-chart-widget',
    width:750,
    height:500,
    layout:'fit',
    items:[
        {xtype:'bar-charts'},
    ],
})
