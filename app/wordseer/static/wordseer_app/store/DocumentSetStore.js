/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Holds the the user's collections of documents.
*/
Ext.define('WordSeer.store.DocumentSetStore', {
    extend:'Ext.data.TreeStore',
    requires:[
        'WordSeer.model.DocumentSetModel',
    ],
    model:'WordSeer.model.DocumentSetModel',
    autoLoad: true,
    proxy: {
        type: 'ajax',
        url: ws_project_path + project_id +  '/sets/',
        extraParams: {
            user: getUsername(),
            collectiontype: 'document',
            instance: getInstance(),
            operation: 'list',
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
