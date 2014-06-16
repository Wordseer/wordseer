/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Renders metadata for the currently displayed
visualization or document list. Controlled by
{@link WordSeer.controller.MetadataController}.

Contained within a {@link WordSeer.view.widget.SidePanel}.

Contains sliders and tree panels and whatever other UI component
is appropriate for filtering and displaying metadata.
**/
Ext.define('WordSeer.view.metadata.MetadataPane',{
    extend:'Ext.panel.Panel',
    alias:'widget.metadata',
    requires:[
        'WordSeer.view.metadata.MetadataComboBox',
        'WordSeer.view.metadata.facet.StringFacets',
        'WordSeer.view.metadata.facet.RangeFacet',
        'WordSeer.view.metadata.facet.Facet',
    ],
    layout: {
        type:'accordion',
        hideCollapseTool: true
    },
    width: '100%',
    dockedItems: [
        {
            dock: 'top',
            xtype: 'metadata-combobox'
        }
    ],
    items: [
        {
            xtype: 'panel',
            layout: 'fit',
            itemId: 'strings',
            tools: [
                {type: 'save', action:'export-metadata'},
            ],
        },
        {
            xtype: 'panel',
            itemId: 'ranges',
            autoScroll:true,
            layout: {
                type: 'vbox',
            },
            tools: [
                {type: 'save', action:'export-numerical-metadata'},
            ],
        },
    ],
    initComponent:function(){
        this.oldFormValues = {};
        this.callParent();
        /**
        @event search Fired when the user issues a new search query.
        @param {WordSeer.model.FormValues} formValues a
        formValues object representing a search query.
        The
        {@link WordSeer.controller.MetadataController#respondToSearch
        MetaDataController's respondToSearch} function responds to this event.

        @param {WordSeer.view.metadata.MetadataPane} metadata_pane This metadata
        pane.
        */
        /**
        @event metadataChanged Fired when the user makes a change in the one of the
        metadata browsers.
        @param {WordSeer.model.FormValues} formValues a
        formValues object representing a search query.
        @param {WordSeer.view.metadata.MetadataPane} metadata_pane This metadata
        pane.
        */
        this.addEvents('search', 'metadataChanged');
        this.breadcrumbs = {range:{}, string:{}};
    },

    /** Removes the existing facet views. Used when a new search is issued.
    */
    clear: function() {
        var ranges = this.getComponent('ranges');
        if (ranges) {
            ranges.removeAll();
        }
        var strings = this.getComponent('strings');
        if (strings) {
            strings.removeAll();
        }
    },
    listeners: {
        afterrender: function(view) {
            view.header.insert(1, {
                xtype: 'checkbox',
                name: 'show_language_metadata',
                fieldLabel: 'Language features',
                labelAlign: 'right',
                labelWidth: 100,
            })
            view.header.down('checkbox').setValue(false);
        }
    },
    drawMetadata: function(response){
        if (response) {
            var data = Ext.decode(response.responseText);
            if(data){
                this.data = data.metadata
            }
        }
        this.clear();
        var metadata_property_names = keys(this.data);
        this.stringFacets = [];
        var string_facets_names = [];
        var range_facets_names = [];
        var strings = this.getComponent('strings');
        var ranges = this.getComponent('ranges');
        for(var i = 0; i < metadata_property_names.length; i++){
            var metadata_property_name = metadata_property_names[i];
            var info = this.data[metadata_property_name];
            if(info.type =="string"){
                    this.stringFacets.push(info);
                    string_facets_names.push(info.propertyName);
            } else if (info.type) {
                var ok = true;
                if ((metadata_property_name == "average_word_length"
                    || metadata_property_name == "sentence_length")
                    && !this.header.down('checkbox').getValue()) {
                    ok = false;
                }
                if (ok) {
                    var facet = Ext.create(
                        'WordSeer.view.metadata.facet.RangeFacet',{
                        xtype:'rangefacet',
                        info:info,
                        name:metadata_property_name,
                        itemId:metadata_property_name,
                    });
                    if (!this.getComponent('ranges')) {
                        this.add({
                            xtype: 'panel',
                            itemId: 'ranges',
                            autoScroll:true,
                            layout: {
                                type: 'vbox',
                            },
                            tools: [
                                {type: 'save', action:'export-numerical-metadata'},
                            ],
                        });
                    }
                    ranges = this.getComponent('ranges');
                    this.getComponent('ranges').add(facet);
                    range_facets_names.push(metadata_property_name)
                    facet.draw();
                }
            }
        }
        if(this.stringFacets.length > 0){
            var facet = Ext.create('WordSeer.view.metadata.facet.StringFacets',{
                xtype:'stringfacets',
                info:this.stringFacets,
                name:'Metadata',
                flex: 1,
            });
            if (strings) this.getComponent('strings').add(facet);
        }
        if (string_facets_names.length == 0) {
            if (strings) this.remove(this.getComponent('strings'));
            if (ranges) ranges.expand();
        } else {
            if (strings) strings.setTitle(string_facets_names.join(", "));
        }
        if (range_facets_names.length == 0) {
            if (ranges) this.remove(this.getComponent('ranges'));
            if (strings) strings.expand();
        } else {
            if (ranges) ranges.setTitle(range_facets_names.join(", "));
        }
    },
})
