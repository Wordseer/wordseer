/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
// Put all the Google closure library requires in here, because they actually
// rewrite and refresh the page. Need to get them all in before the app
// starts.
// For assembling the HTML of a document in the DocumentViewer.
goog.require('goog.string.StringBuffer');

// Begin ExjtJS initialization.
Ext.Loader.setPath({
    // TODO: hardcoding this path is a hack - 'wordseer/' shouldn't be necessary
    'WordSeer': ws_path
});

Ext.Loader.setConfig({
    disableCaching: false
});

Ext.application({
    name: 'WordSeer',
    // TODO: hardcoding this path is a hack - 'wordseer/' shouldn't be necessary
    appFolder: ws_path,
    requires: [
        'WordSeer.view.windowing.viewport.Viewport',
        'WordSeer.view.table.Table',
        'WordSeer.view.user.SignIn',
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
        'SetsController',
        'SentenceListController',
        'WindowingController',
        'WordMenuController',
        'PhraseSetsController',
        'WordTreeController',
        'WordFrequenciesController',
        'UserController'
    ],
    launch: function() {
        sessionStorage['username'] =  'test';
        APP = {
            getSearchableWidgets: function() {
                return [
                'search-widget',
                'column-vis-widget',
                'word-tree-widget',
                'word-frequencies-widget',
                'bar-charts-widget',
                'sentence-list-widget',
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
                                    text: 'Word Frequencies',
                                },
                                {
                                    widget_xtype: 'search-widget',
                                    text: 'Grammatical Relations',
                                },
                                {
                                    widget_xtype: 'sentence-list-widget',
                                    text: 'Sentences',
                                },
                                {
                                    widget_xtype: 'document-browser-widget',
                                    text: 'Documents',
                                }]
            },
            getWidgets: function() {
                return [
                    {
                        widget_xtype: 'search-widget',
                        text: 'Search',
                        inputClass: [
                            'word',
                            'phrase-set',
                            'grammatical'
                        ]
                    },
                    {
                        widget_xtype: 'word-frequencies-widget',
                        text: 'Word Frequencies',
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
            items:{
                    xtype: 'usersignin',
            }
        });
    }
});
