/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Represents a set of words.

@cfg {String} words A space-separated string concatenation of the words in the
word set.

@cfg {String} iconCls A class for the icon this word set should have when
appearing in a treepanel or  list view.
**/
Ext.define('WordSeer.model.PhraseSetModel', {
    extend:'WordSeer.model.SubsetModel',
    fields:[
        {name: 'phrases', type: 'auto', defaultValue:[]},
        {name:'iconCls', type:'string', defaultValue:'phrase-sets-window'},
    ],
    subsetType:'phrase',

    /** Returns the class of this model. Used by the
    {@link WordSeer.controller.SearchController#searchWith} method to determine
    how to use this item if it's passed in as part of a search query.
    */
    getClass:function(){
        return this.items.length === 0 ? 'empty-phrase-set':'phrase-set';
    },

    /** Reads the contents of this word set from the server and then executes
    the passed-in callback (if provided).
    @param {Function} callback The function to execute after the word set contents
    have been read from the server.
    */
    refresh: function(callback, scope) {
      var read_operation = new Ext.data.Operation({
        action: 'read',
        params: {
          type: 'read',
          id: this.get('id'),
        },
      });
      this.getProxy().read(read_operation, function(operation) {
        var data = Ext.decode(operation.response.responseText);
        this.set('phrases', data.phrases);
        this.set('text', data.text);
        this.set('id', data.id);
        if (scope) {
            callback.call(scope);
        }
      }, this);
    },

    /** Asks the server to remove the given words from this word set, and
    then calls the given callback in the given scope.

    @param {String} phrases The space-separated list of words to remove
    from this word set.
    @param {Function} callback The callback to execute after this operation
    completes.
    @param {Object} scope The scope in which to execute the callback function.
    */
    removePhrases:function(phrases, callback, scope){
        var remove_operation = new Ext.data.Operation({
            action: 'read',
            params: {
              type: 'update',
              update: 'delete',
              id: this.get('id'),
              item: phrases.join("___")
            },
        });
        this.getProxy().update(remove_operation, callback, scope);
        this.commit();
    },

    /** Asks the server to add the given words to this word set and then calls
    the given callback in the given scope.

    @param {String} phrases The space-separated list of words to add to
    this word set.
    @param {Function} callback The callback to execute after this operation
    completes.
    @param {Object} scope The scope in which to execute the callback function.
    */
    addPhrases: function(phrases, callback, scope){
        var add_operation = new Ext.data.Operation({
            action: 'read',
            params: {
              type: 'update',
              update: 'add',
              id: this.get('id'),
              item: phrases.join("___")
            },
        });
        this.getProxy().update(add_operation, callback, scope);
        this.commit();
    },

    /** Updates the contents of this word set to equal the passed-in input.
    Removes any words that are no longer in the set, and adds words that are not
    in it.

    @param {String} wordInput The space-separated list of words to remove
    from this word set.
    @param {Function} callback The callback to execute after this operation
    completes.
    */
    updatePhraseSetValues: function(wordInput, callback, scope){
        var existing_words = this.get('phrases').map(function(phrase){
            return phrase.trim().toLowerCase();
        });
        var phrases = wordInput.split(",").map(function(phrase){
            return phrase.trim().toLowerCase();
        });
        var global = Ext.getStore('PhraseSetStore').getById(this.get("id"));
        var toRemove = [];
        var toAdd = [];
        // remove words that are no longer in the list
        for(var i = 0; i < existing_words.length; i++){
            if(!phrases.contains(existing_words[i])){
                toRemove.push(existing_words[i]);
            }
        }
        // add words that weren't in the old list
        for(var i = 0; i < phrases.length; i++ ){
            if(!existing_words.contains(phrases[i])){
                toAdd.push(phrases[i]);
            }
        }
        global.set('phrases', phrases);
        this.set('phrases', phrases);
        this.removePhrases(toRemove, function(){
              this.addPhrases(toAdd, function(){
                  this.refresh(callback, scope);
              }, this);
          }, this);
      }
});
