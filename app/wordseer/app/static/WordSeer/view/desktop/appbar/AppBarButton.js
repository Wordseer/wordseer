/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.appbar.AppBarButton',{
    extend: 'Ext.Component',
    alias:'widget.appbar-button',
    config:{
        text:null,
        module:null,
    },
    width:32,
    autoEl:{
        tag:'img'
    },
    constructor:function(cfg){
        this.initConfig(cfg);
        imgInfo = {
            src:'../../style/icons/'+this.getModule()+'.png',
            cls: 'wordseer-appbar-button',
        },
        this.autoEl = Ext.apply({}, imgInfo, this.autoEl);
        this.tip = Ext.create('Ext.tip.ToolTip', {
            html: '<span class="wordseer-appbar-text">'+this.getText()+'</span>',
            shadow:false,
            defaultAlign:'l-r',
            showDelay:0,
            hideDelay:0,
            dismissDelay:0,
            cls:'wordseer-appbar-tip',
            width: 300,
        });
        this.callParent(arguments);
       
    },
    listeners:{
        render: function(c){
            c.getEl().on('click', function(){this.fireEvent('click');}, c);
            c.getEl().on('mouseenter', function(){this.fireEvent('hover');}, c);
            c.getEl().on('mouseout', function(){this.fireEvent('hoverEnd');}, c);
            
        },
        click:function(){
           var moduleName = this.getModule();
           var module = APP.getModule(moduleName);
           module.createWindow();
        },
        hover:function(){
            this.tip.setTarget(this.getEl());
            this.tip.show();
            this.tip.showBy(this.getEl());
        },
        hoverEnd:function(){
            this.tip.hide();
        }
    },
})