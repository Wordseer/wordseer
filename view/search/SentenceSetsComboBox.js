/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.view.search.SentenceSetComboBox',{
    requires: [ 'WordSeer.view.search.DocumentSetsComboBox' ],
    extend:'WordSeer.view.search.DocumentSetsComboBox',
    alias:'widget.sentence-collections-combobox',
    initComponent:function(){
        this.callParent();
        this.store = SENTENCE_COLLECTIONS_LIST_STORE;
        this.store.refreshStore();
    },
});
