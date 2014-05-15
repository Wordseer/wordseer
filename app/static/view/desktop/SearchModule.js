/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.SearchModule',{
    extend:'WordSeer.view.desktop.Module',
    requires:[
        'WordSeer.view.visualize.barchart.BarCharts',
        'WordSeer.view.sentence.SentenceList',        
        'WordSeer.view.widget.Widget',
    ],
    id:'search',
    inputClass:['word', 'grammatical'],
    text:'Search',
    initComponent:function(){
        this.makeLauncher();
    },
    createWindow:function(values){
        var desktop = APP.getDesktop();
        var n = WordSeer.view.widget.Widget.instanceCount;
        win = desktop.createWindow({
            id: 'widget-'+n,
            title:'Search',
            width:800,
            height:700,
            isPoppedOut:true,
            layout:'border',
            defaults:{
                resizable:true,
                collapsible:true,
            },
            items:[
               {xtype:'bar-charts', region:'north', height:'300'}, //TODO uncomment?
               {xtype:'sentence-list', region:'center', /*height:'400'*/},
            ],
        }, WordSeer.view.widget.Widget);
        win.show();
        return win;
    }
}
)
