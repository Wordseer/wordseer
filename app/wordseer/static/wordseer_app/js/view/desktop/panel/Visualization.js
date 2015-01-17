/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.panel.Visualization',{
    extend:'Ext.Component',
    alias:'widget.visualization',
    initComponent:function(){
        this.callParent(arguments);
    },
    autoScroll:true,
    config:{
        isWidget:false,
        isVisualization:true,
    },

})