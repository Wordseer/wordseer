/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.SentenceListModule',{
    extend:'WordSeer.view.desktop.Module',
    requires:[
        'WordSeer.view.widget.SentenceListWidget',
      ],
    id:'sentence-list',
    inputClass:['word', 'grammatical', 'phrase-set'],
    text:'Search Sentences',
    widgetClass:'WordSeer.view.widget.SentenceListWidget',
});
