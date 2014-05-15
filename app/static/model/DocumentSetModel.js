/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.model.DocumentSetModel', {
    extend:'WordSeer.model.SubsetModel',
    fields:[
        {name:'allowDrag', type:'boolean', defaultValue:true},
        {name:'allowDrop', type:'boolean', defaultValue:true},
        {name:'iconCls', type:'string', defaultValue:'document-browser-16'},
    ],
    subsetType:'document',
    getClass:function(){
        return this.items.length == 0 ? 'empty-document-set':'document-set';
    },
})
