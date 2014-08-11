/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.Module', {
    mixins: {
        observable: 'Ext.util.Observable'
    },
    config:{
        inputClass:[], // 'word', 'grammatical', or something else
        text:'',
        widgetClass:false,
        iconCls:'icon-grid',
    },
    constructor: function (config) {
        this.mixins.observable.constructor.call(this, config);
        this.inputClass = this.getInputClass();
    },
    createWindow:function(){
        var desktop = APP.getDesktop();
        var unique_id = Ext.id();
        win = desktop.createWindow({
            id: this.id+'-widget-'+unique_id,
            isPoppedOut:true,
        }, this.getWidgetClass());
        win.show();
        return win;    
    },
});