/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.view.collections.SentenceSetList',{
    extend:'WordSeer.view.collections.subsets.SubsetsList',
    alias:'widget.sentence-collections-list',
    requires:[
        'WordSeer.store.SentenceSetStore',
    ],
    title:'Sentence Sets',
    store: 'SentenceSetStore',
});
