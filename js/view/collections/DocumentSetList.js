/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.view.collections.DocumentSetList', {
    extend:'WordSeer.view.collections.subsets.SubsetsList',
    alias:'widget.collections-list',
    requires:[
        'WordSeer.store.DocumentSetStore',
    ],
    title:'Document Sets',
    store: 'DocumentSetStore',
});
