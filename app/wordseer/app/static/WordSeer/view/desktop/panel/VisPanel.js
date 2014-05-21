/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.panel.VisPanel',{
    extend:'Ext.panel.Panel',
    alias:'widget.visualization',
    autoScroll:true,
    config:{
        isWidget:false,
        isVisualization:true,
    },
    tools:[
        //1.pop-out tool: Pops the visualization out into another window.
        {
            type:'maximize',
            listeners:{
                click:function(){
                    var title = this.up('panel').title;
                    var formValues = this.up('window')
                        .down('form')
                        .getForm()
                        .getValues();
                    var widget = this.up('panel').launcher.createWindow();
                    widget.fireEvent('search', formValues);
                    widget.down('form').getForm().setValues(formValues);
                }
            }
        },
    ],
    initComponent:function(){
        //this.on('afterrender', this.handleHeader);
        this.addEvents('search');
        this.callParent(arguments);
    },
    handleHeader:function(){
        this.parentElement = this.findParentByType('window');
        this.isAlone = this.parentElement.items.getCount() == 1;
        this.showHideHeader();
    },
    showHideHeader: function(){
        if(this.isAlone){
            this.getHeader().hide();
        }else{
            this.getHeader().show();
        }
    },
})