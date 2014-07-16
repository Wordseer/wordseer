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
      url:'../../src/php/subsets/crud.php',
      extraParams:{
         type:'listflat',
         collectiontype:'document',
         instance:getInstance(),
         user: getUsername(),
      },
      reader:'json',
    },
    constructor: function(config) {
      this.callParent(arguments);
      this.getProxy().setExtraParam('user', getUsername());
    }
});
