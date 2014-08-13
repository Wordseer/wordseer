/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A flat-list format store of all the word sets in WordSeer. Each instance of
a {@link WordSeer.view.search.PhraseSetComboBox} has one of these as its backing
store.
*/
Ext.define('WordSeer.store.PhraseSetListStore', {
    extend:'Ext.data.Store',
    requires:[
        'WordSeer.model.PhraseSetModel',
    ],
    model: 'WordSeer.model.PhraseSetModel',
    proxy: {
      type: 'ajax',
      url:'../../src/php/subsets/crud.php',
      extraParams:{
         type:'listflat',
         collectiontype:'phrase',
         instance:getInstance(),
         user: getUsername(),
      },
      reader: 'json',
    },
    constructor: function() {
      this.callParent(arguments);
      this.getProxy().setExtraParam('user', getUsername());
    }

});
