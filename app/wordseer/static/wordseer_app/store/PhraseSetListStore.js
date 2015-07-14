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
    autoLoad: true,
    model: 'WordSeer.model.PhraseSetModel',
    proxy: {
      type: 'ajax',
      url: ws_project_path + project_id +  '/sets/',
      extraParams:{
         operation:'listflat',
         collectiontype:'phrase',
      },
      reader: {
          type: 'json',
          root: 'results',
      },
    },
    constructor: function() {
      this.callParent(arguments);
    }

});
