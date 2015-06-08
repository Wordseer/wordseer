/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.store.SentenceSearchResultStore', {
    extend:'Ext.data.Store',
    model: 'WordSeer.model.SentenceSearchResultModel',
    autoDestroy: true,
    proxy:{
        type: 'ajax',
        noCache: false,
        timeout: 9000000,
        url: ws_api_path + ws_project_path + project_id + '/sentences',
        reader: {
            type: 'json',
            root: 'results',
            totalProperty: 'total'
        }
    },
    constructor: function(config) {
        this.callParent(arguments);
    }
});
