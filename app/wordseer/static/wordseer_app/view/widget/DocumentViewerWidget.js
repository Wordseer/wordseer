/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A widget for reading a document
*/
Ext.define('WordSeer.view.widget.DocumentViewerWidget', {
	extend: 'WordSeer.view.widget.Widget',
	requires:[
        'WordSeer.view.document.ContentsPane',
        'WordSeer.view.document.DocumentViewer',
    ],
    alias: 'widget.document-viewer-widget',
    items:[
        {xtype:'document-viewer', region:'center', itemId:'viewer'},
     ],
})
