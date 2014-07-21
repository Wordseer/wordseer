/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
WordSeer.SubsetModel The base class for all collection-like
models in WordSeer:
    - {WordSeer.model.PhraseSetModel}
    - {WordSeer.model.DocumentSet}

The basic interactions and state for a subset displayed
in a SubsetList tree panel

Inheritors:
    - {@link WordSeer.model.collections.DocumentSetsModel}
    - {@link WordSeer.model.PhraseSetModel}

@cfg {String} text The title of this set.
@cfg {Integer} id The id of this set.
@cfg {Date} date The creation date of this set, in the format 'Y-m-d H:i:s'.
**/
Ext.define('WordSeer.model.SubsetModel', {
    extend:'Ext.data.Model',
    proxy: {
        type: 'ajax',
        url: '../../src/php/subsets/crud.php',
        extraParams: {
            instance: getInstance(),
            type: 'read',
            user: getUsername(),
        },
        reader:'json',
    },
    fields: [
        {name:'text', type:'string'},
        {name:'id', type:'int'},
        {name: 'ids', type:'auto'},
        {name:'date', type:'date', dateFormat:'Y-m-d H:i:s', defaultValue:0},
        {name:'sentence_count', type:'int', defaultValue:0},
        {name:'document_count', type:'int', defaultValue: 0},
    ],
    config:{
        subsetType:'',
        items: [],
    },

    statics: {
        /**
        @static {Function} colors A function that takes in an integer and outputs
        a six-digit hexadecimal representation of a color.
        */
        colors: SUBSETS_COLOR_SCALE,  // In util.js.

        /**
        @static {Function} makeSubsetTag A function that returns the HTML of a
        small breadcrumb-like "tag" denoting the set to which an item belongs.
        When clicked, it triggers the 'subsetTagClicked' event on a widget.
        @param {Integer} id The id of the subset
        @param {String} text The name of the subset
        @param {String} tag_html The html of a small subset tag, that, when
        clicked, opens up the subset for editing.
        */
        makeSubsetTag: function(id, text) {
            var color = WordSeer.model.SubsetModel.colors(id);
            var rgb = d3.rgb(color);
            var representation = "rgba("+rgb.r+","+rgb.g+","+rgb.b+",0.2)";
            if (!text) {
                text = WordSeer.model.SubsetModel.getText(id);
            }
            var onclick = "Ext.ComponentQuery.query(\"widget\")[0]" +
                ".fireEvent(\"subsetTagClicked\", " + id + ")";
            var html = "<span class='breadcrumb set-tag' "
                + " onclick='" + onclick + "' "
                + " style='background-color:" + representation + ";'>"
                + text
                + "</span>";
            return html;
        },

        /**
        @static {Function} getText A function that returns the name of the set
        with the given ID.
        @param {Integer} id The id of the subset
        @param {String} text The name of the subset with the given ID.
        */
        getText: function(id) {
            var text = "";
            if (Ext.getStore("DocumentSetStore").getById(id)) {
                text = Ext.getStore("DocumentSetStore").getById(id)
                    .get("text");
            } else if (Ext.getStore("SentenceSetStore").getById(id)) {
                text = Ext.getStore("SentenceSetStore").getById(id)
                    .get("text");
            } if (Ext.getStore("PhraseSetStore").getById(id)) {
                text = Ext.getStore("PhraseSetStore").getById(id)
                    .get("text");
            }
            return text;
        },
    },

    /** Returns the title of this set, only exists for compatibility with the
    {@link WordSeer.model.WordModel}. A set can be used instead of a word in
    search queries, so they must present a similar set of outward-facing
    methods.

    @return {String} The title of this set.
    */
    getWord:function(){
        return this.get('text');
    },
    resetClass:function(){
        return false;
    },

    /** Asks the server to create a new set of the same type as this model with
    the given name then executes the given callback in the given scope.

    @param {Function} callback The callback to execute after this operation
    completes.
    @param {Object} scope The scope in which to execute the callback function.
    @param {String} name The name of the new set.
    */
    newSet:function(callback, scope, name){
        if (!name) {
            name = '{New Group}';
        }
        if (name[0] != "{") {
            name = "{"+name;
        }
        if (name[name.length-1] != "}") {
            name = name + "}";
        }
        var create_operation = new Ext.data.Operation({
            action: 'read',
            params:{
                type:'create',
                name: name,
                parent:this.get('id'),
                collectiontype:this.getSubsetType(),
                user: getUsername(),
            },
        });
        this.getProxy().create(create_operation, callback, scope);
        Ext.getCmp('windowing-viewport').fireEvent('setchanged');
    },

    /** Asks the server to delete this set then executes the given callback in
    the given scope.

    @param {Function} callback The callback to execute after this operation
    completes.
    @param {Object} scope The scope in which to execute the callback function.
    */
    delete: function(callback, scope){
        var delete_operation = new Ext.data.Operation({
            action: 'read',
            params:{
                type:'delete',
                id: this.get('id'),
                user: getUsername(),
            },
        });
        this.getProxy().destroy(delete_operation, callback, scope);
        Ext.getCmp('windowing-viewport').fireEvent('setchanged');
    },

    /** Asks the server to rename this set to the given name then executes the
    given callback in the given scope.

    @param {String} new_name The new name.
    @param {Function} callback The callback to execute after this operation
    completes.
    @param {Object} scope The scope in which to execute the callback function.
    */
    rename:function(new_name, callback, scope){
        if (new_name[0] != "{") {
            new_name = "{"+new_name;
        }
        if (new_name[new_name.length-1] != "}") {
            new_name = new_name + "}";
        }
        var rename_operation = new Ext.data.Operation({
            action: 'read',
            params:{
                type:'update',
                update: 'rename',
                id: this.get('id'),
                newName: new_name,
                user: getUsername(),
            },
        });
        this.set('text', new_name);
        this.getProxy().update(rename_operation, callback, scope);
        Ext.getCmp('windowing-viewport').fireEvent('setchanged');
    },

    /** Asks the server to return the contents of this set, updates the fields
    of this set to reflect that.
    */
    read:function(){
        var read_operation = new Ext.data.Operation({
            action: 'read',
            params:{
                type:'read',
                id: this.get('id'),
                user: getUsername(),
            },
        });
        this.getProxy().read(read_operation);
    },

    /** Asks the server to remove the given id's from this set, and
    then calls the given callback in the given scope.

    @param {Array} ids The list of ids to remove from this set.
    @param {Function} callback The callback to execute after this operation
    completes.
    @param {Object} scope The scope in which to execute the callback function.
    */
    removeItems:function(ids, callback, scope){
        var remove_operation = new Ext.data.Operation({
            action: 'read',
            params: {
              type: 'update',
              update: 'delete',
              id: this.get('id'),
              item: ids.join("___"),
            },
        });
        this.getProxy().update(remove_operation, callback, scope);
        var numeric = ids.filter($.isNumeric);
        if (numeric.length > 0) {
            var me = this;
            var mine = me.get('ids').map(function(x){return parseInt(x.id);});
            numeric.forEach(function(id) {
                for(var i = 0; i < mine.length; i++){
                    if (id == mine[i]){
                        me.get('ids').splice(i, 1);
                    }
                }
            });
        }
        this.commit();
        Ext.getCmp('windowing-viewport').fireEvent('setchanged');
    },

    /** Asks the server to add the given ID's to this set and then calls the
    given callback in the given scope.

    @param {Array} ids The list of ids to add to this set.
    @param {Function} callback The callback to execute after this operation
    completes.
    @param {Object} scope The scope in which to execute the callback function.
    */
    addItems:function(ids, callback, scope){
        var add_operation = new Ext.data.Operation({
          action: 'read',
          params: {
            type: 'update',
            update: 'add',
            id: this.get('id'),
            item: ids.join("___"),
          },
        });
        this.getProxy().update(add_operation, callback, scope);
        var numeric = ids.filter($.isNumeric);
        if (numeric.length > 0) {
            var mine = this.get('ids').map(function(x){return parseInt(x.id);});
            var me = this;
            numeric.forEach(function(id) {
                if (mine.indexOf(id) == -1) {
                    me.get('ids').push({id:id});
                }
            });
        }
        this.commit();
        Ext.getCmp('windowing-viewport').fireEvent('setchanged');
    },

    /** Get a unique color based on this subset's ID
    @return {String} hex a six-digit hexadecimal representation of this subset's
    color.
    */
    getColor: function() {
        var id  = this.get('id');
        if (id) {
            return this.self.colors(parseInt(id));
        }
    },
});
