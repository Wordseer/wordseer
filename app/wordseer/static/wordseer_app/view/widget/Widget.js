/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Widgets are the base class for all views in WordSeer that display
information about the text collection from the server.

A Widget's main job is to display a history item. By default, a Widget also
contains the following components for browsing and filtering the display and
for keeping track of the browsing and filtering state:
- {@link WordSeer.view.search.BreadCrumbsPane} For displaying and manipulating
the current searches and filters applied to the Widget. The
{@link WordSeer.controller.BreadCrumbsController} listens for activity on this
component.
- {@link WordSeer.view.widget.SidePanel} For displaying and allowing the
user to filter by hierarchical metadata categories that match the current search
(or, if there is no search, displaying all available metadata categories). The
{@link WordSeer.controller.MetadataController} listens for activity on this
component and fetches metadata categories from the server whenever a new search
is performed.
- {@link WordSeer.view.phrases.PhrasesList} For displaying and allowing the user
to filter the Widget by frequent two-word-or-longer phrases that match the
current search. The {@link WordSeer.controller.PhrasesController} listens for
activity on this component and fetches frequent phrases from the server whenever
a new search is performed.
- Three {@link WordSeer.view.frequentwords.FrequentWordsList}s, one each for
Nouns, Verbs, and Adjectives, for displaying and allowing the user to filter
the Widget by frequent words.

Currently, only the search and visualization widgets use these components. In
the other types of widgets, they are absent.

WordSeer currently has the following Widgets:

- Visualization
    - {@link WordSeer.view.visualize.wordtree.WordTreeWidget Word Tree}
    - {@link WordSeer.view.visualize.barchart.BarChartWidget Bar Charts}
    - {@link WordSeer.view.visualize.columnvis.ColumnVisWidget ColumnVis}
- Search
    - {@link WordSeer.view.widget.SearchWidget Search}
    - {@link WordSeer.view.widget.DocumentBrowserWidget Document Browser}
- Grouping and Organizing
    - {@link WordSeer.view.widget.PhraseSetsWidget Word Sets}
-  Reading
    - {@link WordSeer.view.widget.DocumentViewerWidget}
*/
Ext.define('WordSeer.view.widget.Widget',{
    //extend:'Ext.window.Window',
    extend: 'Ext.Container',
    alias:'widget.widget',
    requires: [
        'WordSeer.view.frequentwords.FrequentWordsList',
        'WordSeer.view.phrases.PhrasesList',
        'WordSeer.view.search.BreadCrumbsPane',
    ],
    autoEl: {
        cls: 'div'
    },
    config:{
        /**
        @cfg {WordSeer.model.HistoryItemModel} historyItem The history item
        currently being displayed by this Widget.
        */
        historyItem: false,

        /**
        @cfg {WordSeer.model.FormValues} formValues The current state of the
        widget's search query. If any components within a widget want to modify
        the search query and re-issue it, they must store the new values in
        this field before firing the {@link #searchParamsChanged} event.
        */
        formValues: {}

    },
    initComponent:function(){
        /**
        @event searchParamsChanged
        Fired by components within this widget whenever the user performs a
        search or browsing action that necessitates a change in the data
        displayed by this widget. The
        {@link WordSeer.controller.SearchController#searchParamsChanged} method
        listens for this event and responds to it by calculating the new search
        parameters and {@link WordSeer.model.HistoryItemModel history item}
        (based on the user's interactions with the widget) and telling the
        widget to issue a new search with the updated history item.

        @event subsetTagClicked
        Fired when the user clicks on a subset tag somewhere in the app.
        @param {Integer} id The id of the subset whose tag was clicked.
        */
        this.addEvents('searchParamsChanged', 'subsetTagClicked');
        this.callParent(arguments);
    },
});
