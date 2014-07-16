/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.view.collections.words.PhraseSetWord', {
    extend:'Ext.container.Container',
    requires:[
        'WordSeer.view.Word',
    ],
    alias:'widget.PhraseSetword',
    autoEl:{
        tag: 'span',
        cls: 'phrase-set-word',
    },
    config:{
        word:false,
        PhraseSet:false,
    },
    initComponent: function(cfg){
        var items = [
            {
                xtype:'button',
                iconCls:'close-btn',
                width:12,
                height:12,
                itemId:'close-button',
                hidden:true,
                handler:function(){
                    var button = this;
                    button.up('window')
                        .removeWord(button.up().itemId);
                    button.up().up().remove(button.up());
                }
            },
            this.getWord(),
        ];
        this.items = items;
        this.callParent(arguments);
    },
    listeners:{
        afterrender:function(thisComponent){
            this.getEl().on('mouseover', function(){
                thisComponent.fireEvent('mouseover');
            });
            this.getEl().on('mouseout', function(){
                    thisComponent.fireEvent('mouseout');
             })

        },
        // Marti finds the mouseover and mouseout
        // distracting, let's just hide
        //it for now till we think of something else
        mouseover:function(){
            //this.getComponent('close-button').show();*/
        },
        mouseout:function(){
            //this.getComponent('close-button').hide();
        }
    }
})
