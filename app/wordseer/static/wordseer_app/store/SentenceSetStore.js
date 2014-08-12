/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Holds the user's set of Sentence groups.
*/
Ext.define('WordSeer.store.SentenceSetStore', {
    extend:'Ext.data.TreeStore',
    requires:[
        'WordSeer.model.SentenceSetModel',
    ],
    model:'WordSeer.model.SentenceSetModel',
    autoLoad: true,
    proxy: {
        type: 'ajax',
        url: ws_api_path + 'sets/',
        extraParams: {
            user: getUsername(),
            collectiontype: 'sentence',
            instance: getInstance(),
            type: 'list',
        },
        reader: {
            type: 'json',
            root: 'children',
        }
    },
    root:{
        text:'Groups of Sentences',
        children:[],
        id:0,
        expanded:true,
    },
});
