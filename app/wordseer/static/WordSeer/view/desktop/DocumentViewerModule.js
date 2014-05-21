/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.DocumentViewerModule',{
    extend:'WordSeer.view.desktop.Module',
    inputClass:['word-in-sentence', 'sentence'],
    requires:[
        'WordSeer.view.document.DocumentViewerPanel',
     ],
    id:'document-viewer',
    text:'View Document',
    createWindow:function(){
        var desktop = APP.getDesktop();
        var n = WordSeer.view.document.DocumentViewerPanel.instanceCount;
        win = desktop.createWindow({
            items:[{xtype:'document-viewer-panel'}],
            width:500,
            height:500,
            layout:'fit',
            id: 'document-viewer-'+n,
            title:'View Document'
        });
        win.show();
        win.addListener('resize', function(){
                 console.log('window resized');
        })
        return win;
    }
});
