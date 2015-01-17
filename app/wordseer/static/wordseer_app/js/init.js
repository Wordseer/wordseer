/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
// Put all the Google closure library requires in here, because they actually
// rewrite and refresh the page. Need to get them all in before the app
// starts.
// For assembling the HTML of a document in the DocumentViewer.
goog.require('goog.string.StringBuffer');

// Begin ExjtJS initialization.
Ext.Loader.setPath({
	'WordSeer': '../../src/js',
	'Ext.ux.desktop':'../../lib/desktop/js',
	'MyDesktop':'../../lib/desktop',
	'Skirtle':'../../lib/skirtle', //<- component column files
});

Ext.Loader.setConfig({
    disableCaching: false
});

/**
@class WordSeer
The App definition, following the [ExtJS MVC application architecture](
http://docs.sencha.com/ext-js/4-0/#!/guide/application_architecture-section-2)
guide.
*/
Ext.application({
    name: 'WordSeer',
    appFolder: '../../src/js',
    requires: [
        'WordSeer.view.widget.DocumentBrowserWidget',
        'WordSeer.view.widget.DocumentViewerWidget',
        'WordSeer.view.widget.SearchWidget',
        'WordSeer.view.widget.PhraseSetsWidget',
        'WordSeer.view.widget.WordFrequenciesWidget',
        'WordSeer.view.visualize.columnvis.ColumnVisWidget',
        'WordSeer.view.visualize.wordtree.WordTreeWidget',
        'WordSeer.view.user.SignIn',
    ],
    controllers: [
        'AutoSuggestController',
        'BreadCrumbsController',
        'ColumnVisController',
        'DataExportController',
        'DocumentsController',
        'HistoryController',
        'MetadataController',
        'PhrasesController',
        'FrequentWordsController',
        'SearchController',
        'SentencePopupController',
        'SentenceListController',
        'SetsController',
        'WindowingController',
        'WordFrequenciesController',
        'WordMenuController',
        'PhraseSetsController',
        'WordTreeController',
        'UserController'
    ],
    launch: function(){
        Ext.create('Ext.container.Viewport', {
            layout: 'fit',
            items:{
                    xtype: 'usersignin',
            }
        });
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
        }
    }
})
