/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
A span tag [Ext.Component](http://docs.sencha.com/ext-js/4-1/#!/api/Ext.Component)
representing a {@link WordSeer.model.WordModel} instance.
*/
Ext.define('WordSeer.view.Word', {
	extend: 'Ext.Component',
	alias:'widget.word',
	requires:[
        'WordSeer.model.WordModel',
    ],
    config:{
        /**
        @cfg {WordSeer.model.WordModel} record The WordModel instance to
        display.
        */
        record: null,
    },
    autoEl:{
        tag: 'span',
    },
    initComponent: function(){
        wordInfo = {
            'word-id':this.getRecord().get('wordID'),
            'position': this.getRecord().get('position'),
            'sentence-id': this.getRecord().get('sentenceID'),
            html:this.getRecord().get('word'),
            cls: this.getRecord().get('class'),
        };
        this.addEvents('click');
        this.autoEl = Ext.apply({}, wordInfo, this.autoEl);
        this.callParent(arguments);
    },
    listeners:{
        /**
        @event click
        Fired when the element is clicked.
        @param {WordSeer.view.Word} word The clicked word.
        */
        render: function(c){
            // Propagate the click from the DOM to this ExtJS component.
            c.getEl().on('click', function(event){
                this.fireEvent('click', this, event);
            }, c);
            // Propagate the click from the DOM to this ExtJS component.
            c.getEl().on('contextmenu', function(event){
                this.fireEvent('contextmenu', this, event);
                return
            }, c);
        },
    },

    /** Removes the highlight that appears when a word menu is shown for
    this word.
    */
    resetClass:function(){
        if (this.getEl()) {
            $(this.getEl().dom).removeClass('menu-word');
        }
    }
})
