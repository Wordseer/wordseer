/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.WordTreeModule',{
    extend:'WordSeer.view.desktop.Module',
    requires:[
        'WordSeer.view.visualize.wordtree.WordTreeWidget',
      ],
    id:'word-tree',
    inputClass:['word', 'grammatical', 'phrase-set'],
    text:'Word Tree',
    widgetClass:'WordSeer.view.visualize.wordtree.WordTreeWidget',
});
