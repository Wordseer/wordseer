/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
// Put all the Google closure library requires in here, because they actually
// rewrite and refresh the page. Need to get them all in before the app
// starts.
// For assembling the HTML of a document in the DocumentViewer.
goog.require('goog.string.StringBuffer');

// Begin ExjtJS initialization.
Ext.Loader.setPath({
    'WordSeer': '../../src/js'
});

Ext.Loader.setConfig({
    disableCaching: false
});

Ext.application({
    name: 'WordSeer',
    appFolder: '../../src/js',
    requires: [
        'WordSeer.view.windowing.viewport.Viewport',
        'WordSeer.view.table.Table',
        'WordSeer.view.user.SignIn',
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
        'SetsController',
        'SentenceListController',
        'WindowingController',
        'WordMenuController',
        'PhraseSetsController',
        'WordTreeController',
        'WordFrequenciesController',
        'UrlHistoryController',
        'UserController'
    ],
    launch: function() {
        sessionStorage['username'] =  'test';
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

        // set up Ext History utility
        // required DOM events
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

        // initialize
        Ext.History.init(function(){
            // if there's a hash in URL, get it
            var hash = document.location.hash;
            console.log("init  hash: " + hash);
            // hand off to url history controller
            // this.getController('UrlHistoryController').fireEvent('tokenchange',
                // hash.replace('#',''));
        });

        // handle history changes
        Ext.History.on('change', function(token){
            // hand off to url history controller for dispatching
            me.getController('UrlHistoryController').dispatch(token);
        });

//      redirect to user sign in 
        Ext.History.add("usersignin");
        
    }
});
