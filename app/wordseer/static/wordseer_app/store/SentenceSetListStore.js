/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.store.SentenceSetListStore', {
    extend:'Ext.data.Store',
    requires:[
        'WordSeer.model.SentenceSetModel',
    ],
    model:'WordSeer.model.SentenceSetModel',
    storeId: 'SentenceSetListStore',
    proxy: {
      type: 'ajax',
      url: ws_api_path + 'sets/',
      extraParams:{
         type:'listflat',
         collectiontype:'sentence',
         instance:getInstance(),
         user: getUsername(),
      },
      reader:  'json',
    },
})
