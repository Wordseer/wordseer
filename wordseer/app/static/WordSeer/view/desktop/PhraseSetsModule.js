/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.PhraseSetsModule',{
    extend:'WordSeer.view.desktop.Module',
    id:'phrase-sets',
    text:'Word Sets',
    inputClass:['phrase-set', 'empty-phrase-set'],
    createWindow:function(values){
        var desktop = APP.getDesktop();
        var w = Ext.getCmp('phrase-sets-window');
        if(!w){
            var win = desktop.createWindow({
                items:[{xtype:'phrase-sets'}],
                layout:'fit',
                id: 'phrase-sets-window',
                iconCls:'phrase-sets-window',
                title:'Browse Word Sets'
            });
            win.show();
            return win;
        } else{
            w.toFront();
        }
    }
});
