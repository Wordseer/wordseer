/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.collections.words.PhraseSetCanvas',{
    extend:'Ext.panel.Panel',
    requires:[
        'WordSeer.view.collections.words.PhraseSet',
    ],
    alias:'widget.PhraseSetcanvas',
    autoScroll:true,
    config:{
        registry:{}
    },
    statics: {
        makeWindowId: function(id) {
            return 'PhraseSet-'+id;
        }
    },
    initComponent:function(){
      this.addEvents('click', 'contextmenu', 'dblclick');
      this.initConfig();
      this.callParent();
      this.setRegistry({});
    },
    listeners:{
        afterrender:function(){
            // make click events on the underlying HTML
            // component register on the panel
            var me = this;
            me.parentPanel = me.up('widget').down('panel');
            this.getEl().on('click', function(e){
                me.fireEvent('click', e);});
            me.getEl().on('contextmenu', function(e){
                me.fireEvent('contextmenu', e);});
            this.getEl().on('dblclick', function(e){
                me.fireEvent('dblclick', e);});
        },
    },
    drawPhraseSet:function(record){
        //disallow duplicate windows
        var id = record.get('id');
        var win_id = this.self.makeWindowId(id);
        var name = record.get('text');
        var win = null;
        if (Ext.getCmp(win_id) == undefined) {
            win = Ext.create('WordSeer.view.collections.words.PhraseSet',{
                name:name,
                id: win_id,
                PhraseSetId: id,
                itemId:win_id,
                record:record,
            });
            this.add(win);
            win.show();
            this.setRandomPosition(win);
        } else {
            win = Ext.getCmp(win_id);
            win.setRecord(record);
            win.update();
        }
        return win;
    },
    setRandomPosition:function(win){
        var totalX = this.getWidth()-150;
        var totalY = this.getHeight()-150;
        var x = totalX*Math.random();
        var y = totalY*Math.random();
        win.setPosition(x,y);
    },
    selectPhraseSet:function(name,id){
       var win = this.openPhraseSet(name, id);
       win.toFront();
    },
    update:function(id){
        if(id){
            if(this.getRegistry()[id]){
                this.getRegistry()[id].update();
            }
        }else{
            var registry = this.getRegistry();
            for(var id in registry){
                if(registry.hasOwnProperty(id)){
                    registry[id].update();
                }
            }
        }

    },
    deletePhraseSets:function(ids){
        for(var i = 0; i < ids.length; i++){
            this.deletePhraseSet(ids[i]);
        }
    },
    deletePhraseSet:function(id){
        if(this.getRegistry()[id]){
            this.getRegistry()[id].destroy();
            delete this.getRegistry()[id];
        }
    },
    getPhraseSetWindow: function(id) {
        return Ext.getCmp(this.self.makeWindowId(id));
    },
})
