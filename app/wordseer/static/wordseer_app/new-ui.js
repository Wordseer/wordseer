/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
// Put all the Google closure library requires in here, because they actually
// rewrite and refresh the page. Need to get them all in before the app
// starts.
// For assembling the HTML of a document in the DocumentViewer.
goog.require('goog.string.StringBuffer');

// Begin ExjtJS initialization.
Ext.Loader.setPath({
    'WordSeer': ws_static_path
});

Ext.Loader.setConfig({
    disableCaching: false
});

Ext.application({
    name: 'WordSeer',
    appFolder: ws_static_path,
    requires: [
        'WordSeer.view.windowing.viewport.Viewport',
        'WordSeer.view.table.Table',
        'Ext.util.History',
    ],
    controllers: [
        'AutoSuggestController',
        'BreadCrumbsController',
        'DataExportController',
        'DocumentsController',
        'FrequentWordsController',
        'HistoryController',
        'MetadataController',
        'PhrasesController',
        'SearchController',
        // 'SetsController',
        'SentenceListController',
        'WindowingController',
        'WordMenuController',
        'TagMenuController',
        // 'PhraseSetsController',
        'WordTreeController',
        'WordFrequenciesController',
        'UrlHistoryController'
    ],
    launch: function() {
        var me = this;
        APP = {
            getSearchableWidgets: function() {
                return [
                'search-widget',
                'column-vis-widget',
                'word-tree-widget',
                'word-frequencies-widget',
                'bar-charts-widget',
                'sentence-list-widget',
                'sentence-table-widget',
                'document-browser-widget',
                'document-viewer-widget']
            },

            getSVGVisualWidgets: function() {
                return [
                'column-vis-widget',
                'word-tree-widget',
                'search-widget',
                'bar-charts-widget',
                'word-frequencies-widget']
            },
            getSwitchableWidgets: function() {
                return [{
                                    widget_xtype: 'word-tree-widget',
                                    text: 'Word Tree',
                                },
                                {
                                    widget_xtype: 'word-frequencies-widget',
                                    text: 'Metadata Profile',
                                },
                                // {
                                //     widget_xtype: 'search-widget',
                                //     text: 'Grammatical Relations',
                                // },
                                {
                                    widget_xtype: 'sentence-list-widget',
                                    text: 'Sentence List',
                                },
                                {
                                    widget_xtype: 'document-browser-widget',
                                    text: 'Document Table',
                                },
                                {
                                    widget_xtype: 'sentence-table-widget',
                                    text: 'Sentence Table',
                                }]
            },
            getWidgets: function() {
                return [
                    // {
                    //     widget_xtype: 'search-widget',
                    //     text: 'Search',
                    //     inputClass: [
                    //         'word',
                    //         'phrase-set',
                    //         'grammatical'
                    //     ]
                    // },
                    {
                        widget_xtype: 'word-frequencies-widget',
                        text: 'Metadata Profile',
                        inputClass: [
                            'word',
                            'phrase-set',
                            'grammatical',
                        ]
                    },
                    {
                        widget_xtype: 'word-tree-widget',
                        text: 'Word Tree',
                        inputClass: [
                            'word',
                            'phrase-set',
                            'grammatical',
                        ]
                    },
                    {
                        widget_xtype: 'document-browser-widget',
                        text: 'Documents',
                        inputClass: [
                            'word',
                            'phrase-set',
                            'grammatical',
                        ]
                    },
                    {
                        widget_xtype: 'phrase-sets-widget',
                        text: 'Word Sets',
                        inputClass: [
                            'phrase-set',
                            'empty-phrase-set',
                        ]
                    }
                ];
            }
        };

        var store_cfg = {fields:['word', 'count']};

        Ext.create('Ext.container.Viewport', {
            layout: 'fit',
            items: {

            }
        });

        // start the main WordSeer application
        // by initializing HistoryItems and Viewport
        // Ext.getStore('HistoryItemStore').getProxy().id = ('HistoryItemStore-' +
        //     getInstance());
        Ext.getStore('HistoryItemStore').load();
        var viewport = Ext.ComponentQuery.query('viewport')[0];
        viewport.removeAll();
        viewport.add({
            xtype: 'windowing-viewport'
        });

        // set up Ext History utility
        // required DOM elements
        me.historyForm = Ext.getBody().createChild({
            tag: 'form',
            action: '#',
            cls: 'x-hidden',
            id: 'history-form',
            children: [{
                tag: 'div',
                children: [{
                    tag: 'input',
                    id: Ext.History.fieldId,
                    type: 'hidden'
                }, {
                    tag: 'iframe',
                    id: Ext.History.iframeId
                }]
            }]
        });

        // initialize history
        Ext.History.init(function(){
            // retrieve the history token from URL
            var token = document.location.hash.slice(1);
            // if no token, just send to landing page
            if (token == "") {
                token = "home"
            }
            me.getController("UrlHistoryController").dispatch(token);
        });

        // handle history changes
        Ext.History.on('change', function(token){
            me.getController("UrlHistoryController").dispatch(token);
        });

    }
});
