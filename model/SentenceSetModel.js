/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Represents a set of sentences.

@cfg {String} iconCls A class for the icon this word set should have when
appearing in a treepanel or  list view.
@cfg {Array} items A list of ids of sentences in this collection.
*/
Ext.define('WordSeer.model.SentenceSetModel', {
    extend:'WordSeer.model.SubsetModel',
    fields:[
        {name:'iconCls', type:'string', defaultValue:'document-browser-16'},
        {name:'type', type:'string', defaultValue:'sentence'},
    ],
    proxy: {
      type: 'ajax',
      url: '../../src/php/subsets/crud.php',
       extraParams: {
          instance: getInstance(),
          type: 'read',
          user: getUsername(),
      },
      reader: 'json',
    },
    subsetType:'sentence',
    getClass:function(){
        return this.items.length == 0 ? 'empty-sentence-set':'sentence-set';
    },

});
