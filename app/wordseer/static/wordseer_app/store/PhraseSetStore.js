/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Holds the user's collection of words.
*/
Ext.define('WordSeer.store.PhraseSetStore', {
    extend:'Ext.data.TreeStore',
    requires:[
        'WordSeer.model.PhraseSetModel',
    ],
    model:'WordSeer.model.PhraseSetModel',
    autoLoad: true,
    proxy: {
        type: 'ajax',
        url: ws_api_path + 'sets/',
        extraParams: {
            user: getUsername(),
            collectiontype: 'phrase',
            instance: getInstance(),
            type: 'list',
        },
        reader: {
            type: 'json',
            root: 'children',
        }
    },
    root:{
        text:'Word Sets',
        children:[],
        id:0,
    },
    listeners: {
        load: function() {
            Ext.getStore('PhraseSetListStore').load(
                {params:{user:getUsername()}});
            Ext.ComponentQuery.query('PhraseSetcombobox').forEach(function(box){
                box.getStore().load({params:{user:getUsername()}});
            });
        },
    }
});
