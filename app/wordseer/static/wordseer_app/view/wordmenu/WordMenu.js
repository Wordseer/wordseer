/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A menu that appears next to words, phrases, and breadcrumbs with options to
search, visualize and see related words, and add to word sets. Controlled by
the {@WordSeer.controller.WordMenuController WordMenuController}.

# Menu Options

The items in the WordMenu change depending on the
{@link WordSeer.model.WordModel#class class} of the passed-in
{@link WordSeer.view.wordmenu.WordMenu#current current} config
{@link WordSeer.view.WordModel WordModel} instance.

The menu always contains options to view the contents of the user's
{@link WordSeer.controller.PhraseSetsController Word Sets}.

## Word and phrase-set options
If the class is either `"word"` or `"phrase-set"`, the menu shows
{@link WordSeer.wordmenu.WordMenuItem search} and
{@link WordSeer.wordmenu.GrammaticalSearchOption grammatical search} options for
issue search queries within each of the widgets in the Application, along with
counts of how often various grammatical constructions exist.
{@img wordmenu/search-options.png Search options in the word menu}

These counts are fetched from `src/php/grammaticalsearch/get-search-options.php`
with a GET request with the following parameters:

    {
        instance: {String} the name of the current instance,
        word: {String} the word or phrase-set ID,
        cls: {String} the class of the menu's {@link #current} WordModel instance
    }

The GET request's callback is the {@link #addSearchOptions} method.

## Other options
Otherwise, if the class is neither `"word"` nor `"phrase-set"`,  the menu shows
{@link WordSeer.view.wordmenu.LauncherButton LauncherButton}s for each widget in
the module.
**/
Ext.define('WordSeer.view.wordmenu.WordMenu', {
    extend:'WordSeer.view.menu.Menu',
    alias:'widget.wordmenu',
    requires:[
        'WordSeer.view.menu.ResultListMenu',
        'WordSeer.view.menu.MenuItem',
        'WordSeer.view.menu.PhraseMenuItem',
        'WordSeer.view.wordmenu.LauncherButton',
        'WordSeer.view.wordmenu.GrammaticalSearchOption',
        'WordSeer.model.WordModel',
    ],
    width: 150,
    config:{
        /**
        @cfg {WordSeer.model.WordModel} current The WordModel instance for
        which to create a menu.
        */
        current:null,
        /**
        @cfg {WordSeer.view.Word | HTMLElement} shownBy The item on the page
        next to which the menu should appear.
        */
        shownBy:null,

        /**
        @cfg {Ext.Component} view The actual component or container to which the
        {@link #shownBy} belongs.
        */
        view: null,

        /**
        @cfg {WordSeer.model.FormValues} formValues The filters to apply to
        restrict the set of sentences for the nearby words.
        */
        formValues:{},

        /**
        @cfg {String} an alignTo position.
        */
        position: 'l-r?',
    },

    initComponent:function(){
        var me = this;
        var current = this.getCurrent();
        var widgets = APP.getWidgets();
        var cls = current.get('class');
        var sentence_id = current.get('sentenceID');

        // The list of menu items that the following code is going to populate
        // with buttons depending on exactly what was clicked.
        var menuItems = [];

        if (sentence_id >= 0) {
            menuItems.push({
                text: "<span class='wordmenu-label'>Sentence</span>",
                menu: {
                    xtype: 'result-list-menu',
                    sentenceId: sentence_id,
                    documentId: me.view.getStore().getById(sentence_id)
                        .get('document_id'),
                    type: 'sentence',
                    seeInContext: (me.view.xtype === 'sentence-list' || me.view.xtype === 'sentence-table')
                },
            });
            menuItems.push({
                text: "<span class='wordmenu-label'>Phrases</span>",
                menu:[],
                itemId: 'phrases'
            });
            // Get the phrases that are at this sentence in this position.
            if (current.get('sentenceID') && (current.get('position') != -1)) {
                Ext.Ajax.request({
                    method: 'GET',
                    disableCaching: false,
                    url: ws_api_path + ws_project_path + project_id +
                        '/containing_sequences',
                    params: {
                        sentence_id: current.get('sentenceID'),
                        start_position: current.get('position') -1
                    },
                    scope: me,
                    callback: me.addPhraseOptions,
                });
            }
        }

        if (cls == 'word') {
            // The option to add this word to a set.
            menuItems.push({
                text: "<span class='wordmenu-label'>Add</span> to set",
                menu: {
                    xtype: 'set-menu',
                    type: 'add',
                    store: Ext.getStore('PhraseSetStore'),
                    ids: [current.get('word')],
                }
            });

            // Are there any sets to which this word belongs? If so, give the
            // option to remove them.
            sets_containing_this_word = [];
            var word = current.get('word');
            Ext.getStore('PhraseSetStore').getRootNode().cascadeBy(function(set) {
                if (set.get('phrases').indexOf(word) != -1) {
                    sets_containing_this_word.push(set);
                }
            });
            if (sets_containing_this_word.length > 0) {
                menuItems.push({
                    text: "<span class='wordmenu-label'>Remove</span> from set",
                    menu: {
                        xtype: 'set-menu',
                        type: 'remove',
                        store: Ext.getStore('PhraseSetStore'),
                        ids: [current.get('word')],
                    }

                });
            }
        }

        if (cls == 'word' || cls == 'phrase-set') {
            if (!current.related && (current.get('id') || current.get('wordID'))) {
                if (!current.get('id')) {
                    current.set('id', current.get('wordID'));
                }
                menuItems.push({
                    text: "<span class='wordmenu-label'>Filter</span> for this word",
                    action: 'filter',
                });
            }
            menuItems.push({
                text: "<span class='wordmenu-label'>Search</span> loading options..",
                itemId: "search-placeholder"
            });
            Ext.Ajax.request({
                method: 'GET',
                disableCaching: false,
                url: ws_api_path + ws_project_path + project_id +
                    '/grammatical_search_options',
                params: {
                    word: (cls == 'word' ?
                        me.current.get('word'):me.curent.get('id')),
                    class: cls,
                },
                scope: me,
                callback: me.addSearchOptions,
            });

        }
        if (cls == "word" || cls == "phrase-set") {
            // query for co-occurring words
            
            // initialize the stores
            me.phrasesStore = Ext.create('WordSeer.store.PhrasesStore');
            me.JStore = Ext.create('WordSeer.store.AssociatedWordsStore', {pos:'Adjectives'});
            me.VStore = Ext.create('WordSeer.store.AssociatedWordsStore', {pos:'Verbs'});
            me.NStore = Ext.create('WordSeer.store.AssociatedWordsStore', {pos:'Nouns'});

            menuItems.push({
                text: "<span class='wordmenu-label'>Loading co-occurring</span> words...",
                itemId: "related-words-placeholder",
            });
            var params = {};
            var search = {};

            // load each store
            if (cls == "word") {
                search.gov = me.current.get('word');
            } else {
                search.gov = me.current.get('id');
            }
            search.govtype = cls;

            params.search = [Ext.JSON.encode([search])];

            Ext.Ajax.request({
                    method: 'GET',
                    disableCaching: false,
                    url: ws_api_path + ws_project_path + project_id +
                    '/associated_words',
                    params: params,
                    scope: me,
                    callback: me.addRelatedWordsOption,
                });
            // me.phrasesStore.load({params: params});

            /**
            // Similar words. We don't compute these in the back end right
            // now.
            if (cls == "word") {
                menuItems.push({
                    text: "<span class='wordmenu-label'>Loading similar</span> words...",
                    itemId: "similar-words-placeholder",
                });
            }
            */
        }

        // If this is a product of a nearby words query, add an option to see
        // the contexts.
        if (current.formValues && current.related) {
            menuItems.push({
                text: 'See co-occurrences',
                action: 'get-nearby-word-matches',
            });
        }
        me.items = menuItems;
        this.callParent(arguments);
    },

    /** Adds a {@link WordSeer.wordmenu.WordMenuItem} for showing a popup
    containing nearby words.

    @param {Object} opts Optional parameters passed in by the caller.
    @param {Boolean} success Whether or not the request completed successfully.
    @param {XmlHttpResponse} response Received from
    `src/php/assocated-words/get-associated-words.php`. The response text
    encodes a JSON object with the fields 'Adjectives', 'Nouns', 'Verbs',
    'Adverbs', each of which is an array containing words of the format
    {id: , word: , score: }. Where 'score' is a number, the number of sentences
    in which  that word appears with the menu word.
    */
    addRelatedWordsOption: function(opts, success, response) {
        if (!success) return console.log('word menu: related words query failed');

        // populate the stores
        var related_words = Ext.decode(response.responseText).Words;
        this.NStore.add(_.where(related_words, {category: 'Nouns'}));
        this.JStore.add(_.where(related_words, {category: 'Adjectives'}));
        this.VStore.add(_.where(related_words, {category: 'Verbs'}));
        // debugger;

        var itemId = "related-words-placeholder";
        var placeholder = this.getComponent(itemId);
        if (placeholder) {
            this.remove(placeholder);
        }
        
        this.add([{
            text: "<span class='wordmenu-label'>See</span> co-occurring words",
            action: 'nearbywords'
        }]);

        /**
        itemId = "similar-words-placeholder";
        placeholder = this.getComponent(itemId);
        if (placeholder && related_words.Synsets.length > 0) {
            this.remove(placeholder);
            this.add([{
            text: "<span class='wordmenu-label'>See</span> similar words",
            action: 'similarwords',
            data: related_words.Synsets,
            items:[],
        }]);
        }
        */
    },

    addPhraseOptions: function(opts, success, response) {
        var itemId = 'phrases';
        var resp = Ext.decode(response.responseText);
        var phrases = resp.results;
        menuItems = [];
        for (var i = 0; i < phrases.length; i++) {
            menuItems.push({
                xtype: 'phrase-menu-item',
                text: phrases[i].sequence,
                sentenceCount: phrases[i].sentence_count,
                phraseId: phrases[i].id
            });
        }
        this.getComponent(itemId).menu = menuItems;
    },

    /** Adds {@link WordSeer.wordmenu.WordMenuItem search} and
    {@link WordSeer.wordmenu.GrammaticalSearchOption grammatical search} options
    to the word menu. There is one main option for each widget, with sub-menus
    to search for each each grammatical relationship.

    @param {Object} opts Optional parameters passed in by the caller.
    @param {Boolean} success Whether or not the request completed successfully.
    @param {XmlHttpResponse} response Received from
    `src/php/grammaticalsearch/get-search-options.php`. The response text
    encodes a JSON object with the following fields:
        search: {Number} The number of times the word appears in the collection
        gov: {Object} With the following format:
            {
                {String} relation:  {Number} count The number of times
                this word appears in this governor (gov) position
                in this relationship.
            }
        dep: {Object} With the same format as above, except indicating that the
            other word appears in the dependent (dep) relation to the menu word.
    */
    addSearchOptions: function(opts, success, response) {
        var itemId = "search-placeholder";
        var placeholder = this.getComponent(itemId);
        if (placeholder) {
            this.remove(placeholder);
        }
        var search_options = Ext.decode(response.responseText);
        var current = this.getCurrent();
        var cls = current.get('class');
        var widgets = APP.getWidgets();
        for (var i = 0; i < widgets.length; i++) {
            var itemId = widgets[i].widget_xtype;
            var text = widgets[i].text;
            if (widgets[i].inputClass.contains(cls)) {

            }
        };


        var sub_menu = [];
        sub_menu.push({
            xtype: "grammaticalsearchoption",
            gov: this.getCurrent().get('word'),
            relation: "",
            current: this.getCurrent(),
            count: search_options.search,
        });
        if (search_options.gov != []) {
        var gov_keys = keys(search_options.gov);
            for (var j = 0; j < gov_keys.length; j++) {
                var sub_items = [];
                var children = search_options.gov[gov_keys[j]].children;
                var dep_keys = keys(children);
                for (var ci = 0; ci < dep_keys.length; ci ++) {
                    sub_items.push({
                        xtype: 'grammaticalsearchoption',
                        gov: this.getCurrent().get('word'),
                        dep: dep_keys[ci],
                        relation: gov_keys[j],
                        count: children[dep_keys[ci]],
                        current: this.getCurrent(),
                    });
                }
                sub_menu.push({
                    xtype: 'grammaticalsearchoption',
                    gov: this.getCurrent().get('word'),
                    relation: gov_keys[j],
                    count: search_options.gov[gov_keys[j]].count,
                    menu: sub_items,
                    current: this.getCurrent(),

                });
            }
        }
        if (search_options.dep != []) {
            var dep_keys = keys(search_options.dep);
            for (var j = 0; j < dep_keys.length; j++) {
                var sub_items = [];
                var children = search_options.dep[dep_keys[j]].children;
                var gov_keys = keys(children);
                for (var ci = 0; ci < gov_keys.length; ci ++) {
                    sub_items.push({
                        xtype: 'grammaticalsearchoption',
                        dep: this.getCurrent().get('word'),
                        gov: gov_keys[ci],
                        relation: dep_keys[j],
                        count: children[gov_keys[ci]],
                        current: this.getCurrent(),
                    });
                }
                sub_menu.push({
                    xtype: 'grammaticalsearchoption',
                    dep: this.getCurrent().get('word'),
                    relation: dep_keys[j],
                    count: search_options.dep[dep_keys[j]].count,
                    menu: sub_items,
                    current: this.getCurrent(),
                });
            }
        }
        this.add({
            text: '<span class="wordmenu-label">Search</span> for this word',
            itemId: itemId,
            menu: sub_menu
        });
    },

    close: function(time) {
        if (this.getShownBy().resetClass === undefined) {
            $(this.getShownBy()).removeClass('menu-word');
        } else {
            this.getShownBy().resetClass();
        }
        this.callParent(arguments);
    }
})
