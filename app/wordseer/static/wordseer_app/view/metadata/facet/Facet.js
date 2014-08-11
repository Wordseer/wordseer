/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Represents a facet of metadata.
*/
Ext.define('WordSeer.view.metadata.facet.Facet',{
    extend:'Ext.Component',
    alias:'widget.facet',
    height:30,
    config:{
        /**
        @cfg {Object} info The information about this of this metadata facet
        received from the server.
        */
        info:[],

        /**
        @cfg {String} name The name of the facet.
        */
        name:"",
    },
    initComponent:function(){
        this.callParent();
        this.addEvents('metadataChanged');
        this.enableBubble('metadataChanged');
        this.selected = null;
    },
    getValue:function(){
        return this.selected;
    }
})
