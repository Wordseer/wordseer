/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.BarChartModule',{
    extend:'WordSeer.view.desktop.Module',
    requires:[
        'WordSeer.view.visualize.barchart.BarChartWidget',
      ],
    id:'bar-chart',
    inputClass:['grammatical', 'phrase-set', 'word'],
    text:'Word Frequencies',
    widgetClass:'WordSeer.view.visualize.barchart.BarChartWidget',
});
