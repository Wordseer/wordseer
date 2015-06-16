/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.UniversalVisualizationModule',{
    extend:'WordSeer.view.desktop.Module',
    requires:[
        'WordSeer.view.visualize.barchart.BarCharts',
        'WordSeer.view.sentence.SentenceList',
        'WordSeer.view.visualize.columnvis.ColumnVis',
        'WordSeer.view.visualize.wordtree.WordTree',
        
        'WordSeer.view.widget.Widget',
    ],
    id:'universal',
    inputClass:['word', 'grammatical'],
    text:'All Visualizations',
    initComponent:function(){
        this.makeLauncher();
    },
    createWindow:function(values){
        var desktop = APP.getDesktop();
        var n = WordSeer.view.widget.Widget.instanceCount;
        win = desktop.createWindow({
            id: 'widget-'+n,
            title:'Search',
            width:1000,
            height:850,
            autoScroll: true,
            isPoppedOut:true,
            layout:'border',
            defaults:{
                resizable:true,
                collapsible:true,
            },
            items:[
               {xtype:'sentence-list', region:'south', flex:2},
               {xtype:'bar-charts', region:'east', flex:1},
               {xtype:'word-tree', region:'center', flex:1},
               {xtype:'column-vis', region:'north', flex:2}, 
            ],
        }, WordSeer.view.widget.Widget);
        win.show();
        return win;
    }
}
)