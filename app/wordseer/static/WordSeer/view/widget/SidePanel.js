/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Displays a sidebar in a {@link WordSeer.view.widget.Widget} containing
filtering options. It contains the following views:
    - {@link WordSeer.view.metadata.MetadataPane}
    - {@link WordSeer.view.collections.DocumentSetList}
    - {@link WordSeer.view.collections.SentenceSetList}
*/
Ext.define('WordSeer.view.widget.SidePanel',{
    extend:'Ext.panel.Panel',
    alias:'widget.widget-side-panel',
    requires:[
        'WordSeer.view.metadata.MetadataPane',
        'WordSeer.view.collections.DocumentSetList',
        'WordSeer.view.collections.SentenceSetList',
    ],
    title:'Filters',
    collapsible:true,
    collapseDirection:'left',
    animCollapse: false,
    width:200,
    layout: {
        type:'accordion',
        align: 'stretch',
        collapseFirst: true,
        titleCollapse: true,
        hideCollapseTool: false
    },
    items:[
        {
            xtype:'metadata',
            itemId:'metadata',
            title: 'Metadata',
            flex:1,
        },
        {
            title: 'Sets',
            flex: 1,
            layout: {
                type:'accordion',
                align: 'stretch',
                collapseFirst: true,
                titleCollapse: true,
                hideCollapseTool: false
            },
            items:[
            {
                xtype:'collections-list',
                itemId:'collections',
                flex:1,
            },
            {
                xtype:'sentence-collections-list',
                itemId:'sentence-collections',
                flex:1,
            },
            {
                xtype:'PhraseSetlist',
                itemId:'phrase-sets',
                flex:1,
                title: 'Word Sets',
            }
            ]
        }
    ],
    initComponent:function(){
        /**
        @event search Fired when the user issues a search query or when this
        view is loaded for the first time.
        @param {WordSeer.model.FormValues} formValues a
        formValues object representing a search query.
        @param {WordSeer.view.widget.SidePanel} metadata_panel This view.

        @event searchParamsChanged Fired when the user changes something
        within the filters in this pane.
        @param {WordSeer.model.FormValues} formValues a
        formValues object representing a search query.
        @param {WordSeer.view.widget.SidePanel} metadata_panel This view.

        */
        this.addEvents('search', 'searchParamsChanged');
        this.enableBubble('searchParamsChanged');
        this.callParent(arguments);
    },
    listeners:{
        search:function(formValues, me){
            me.items.each(function(){
                this.fireEvent('search', formValues, this)
            });
        },
        collapse:function(me) {
            me.setWidth(28);
        },
        expand:function(me) {
            me.setWidth(200);
        }
    },
})
