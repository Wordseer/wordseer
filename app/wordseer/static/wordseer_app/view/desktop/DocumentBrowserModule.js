/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.DocumentBrowserModule',{
    extend:'WordSeer.view.desktop.Module',
    requires:[
        'WordSeer.view.widget.DocumentBrowserWidget',
      ],
    id:'document-browser',
    text:'Search Documents',
    inputClass:['word', 'grammatical', 'word-in-sentence', 'sentence',
    	'phrase-set'],
	widgetClass:'WordSeer.view.widget.DocumentBrowserWidget',
});
