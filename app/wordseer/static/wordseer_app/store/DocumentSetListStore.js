/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.store.DocumentSetListStore', {
    extend:'Ext.data.Store',
    requires:[
        'WordSeer.model.DocumentSetModel',
    ],
    model:'WordSeer.model.DocumentSetModel',
    storeId: 'DocumentSetListStore',
    proxy: {
      type: 'ajax',
      url: ws_project_path + project_id +  '/sets/',
      extraParams:{
         operation:'listflat',
         collectiontype:'document',
      },
      reader: {
          type: 'json',
          root: 'results',
      },
    },
    constructor: function(config) {
      this.callParent(arguments);
    }
});
