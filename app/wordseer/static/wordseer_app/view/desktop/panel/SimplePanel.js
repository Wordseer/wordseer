/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Displays a single widget and tools for navigating search history, adding
other panel, and switching searches between widgets.
*/
Ext.define('WordSeer.view.desktop.panel.SimplePanel',{
    extend:'Ext.container.Container',
    alias:'widget.simple-panel',
    config: {
        /**
        @cfg {WordSeer.model.LayoutPanelModel} layoutPanelModel The model
        instance that holds the history of searches for this layout panel.
        */
        layoutPanelModel: false
    },
    initComponent: function() {
        /**
        @event searchParamsChanged
        Fired by components within this panel whenever the user performs a
        search or browsing action that necessitates a change in the data
        displayed by this widget. The
        {@link WordSeer.controller.SearchController#searchParamsChanged} method
        listens for this event and responds to it by calculating the new search
        parameters and {@link WordSeer.model.HistoryItemModel history item}
        (based on the user's interactions with the widget) and telling the
        widget to issue a new search with the updated history item.
        */
        this.addEvents('searchParamsChanged');
        this.callParent(arguments);
    },
    listeners: {
        afterrender: function(me) {
            me.draw();
        },
    },

    draw: function() {
        this.populate();
    },

    populate: function() {
        var me = this;
        console.log('populating a layout panel');
    }
})
