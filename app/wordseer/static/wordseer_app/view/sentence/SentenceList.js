/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A list of sentences **/
Ext.define('WordSeer.view.sentence.SentenceList',{
    extend:'WordSeer.view.table.Table',
    alias:'widget.sentence-list',
    title:'Search Results',
    requires:[
        'WordSeer.store.SentenceSearchResultStore',
        'WordSeer.view.sentence.Sentence',
        'WordSeer.view.collections.SetsToolbar',
    ],
    checkboxes: true,
    multiSelect: true,
    onlyCheckboxSelect: true,
    options: [
        {
            option: {
                tag: 'span',
                cls: 'button disabled',
                html: 'Add selected to Set',
                action: 'add',
            },
            listeners: [
                {
                    event: 'click'
                },
                {
                    event: 'mouseleave'
                }
            ]
        },
        {
            option: {
                tag: 'span',
                html: 'Remove selected from Set',
                cls: 'button disabled',
                action: 'remove',
            },
            listeners: [
                {
                    event: 'click',
                },
                {
                    event: 'mouseleave'
                }
            ]
        },

    ],
    initComponent: function(){
        this.store = Ext.create('WordSeer.store.SentenceSearchResultStore');
        /**
        @event wordclicked Fired when a word in a sentence is clicked.
        @param {Ext.Element} word_element the clicked-on HTML word.
        */
        this.addEvents('wordclicked');
        this.selModel = new Ext.selection.CheckboxModel({
            checkOnly: true,
        });

        /**
        @event wordclicked Fired when the user clicks a word in this list of
        sentences. Sentences (and words) are rendered by {@link #renderSentence}.

        @param {HTMLElement} word The HTML span element representing the word that
        was clicked. The span has the following attributes:
            word-id: The ID of the word
            sentence-id: the id of the sentence in which the word appears
        The text of the HTML span is the word.
        */
        this.addEvents('search', 'wordclicked', 'tagclicked');

        this.columns = [
            {
                field:'sentence',
                cls:'word-wrap',
                flex:10,
                renderer: this.renderSentence
            }
        ];

        // store this data in instance for sentence renderer metadata
        this.model = this.getStore().model;
        this.base_field_names = this.model.getBaseFieldNames();
        this.all_fields = this.model.getFields();

        // add a "rows loading" placeholder 
        this.autoEl.children.push({
            tag: 'div', 
            cls: 'rowsloading hidden',
            html: '<i class="fa fa-circle-o-notch fa-spin"></i> Loading more sentences ...'
        });

        this.callParent(arguments);

    },

    populate: function() {
        var title = 'Search Results';
        title +=  " (" + this.getStore().getTotalCount() +")";
        this.resetTitle(title);
        this.callParent(arguments);
    },

    /** Draws the sentence. If the sentence is in a sentence set, then underlines
    the sentence in the {@link WordSeer.model.SubsetModel#getColor color} of
    the subset, and adds an annotation about which group it's in.
    @param {Object} sentence The sentence. An object with the properties
    {words:, dep_index:, gov_index:,}
    @param metaData Information about the row
    @param {WordSeer.model.SentenceSearchResultModel} record The search result
    being rendered.
    */
    renderSentence: function(record, field, view){
        var sentence = record.get(field);
        var me = view;
        var html = "<div class='sentence'>" + sentence.words;

        // add sentence set tags
        var sentence_sets = record.get('sentence_set');
        if (sentence_sets && sentence_sets.trim().length > 0) {
            var sets = sentence_sets.trim().split(" ");
            for (var j = 0; j < sets.length; j++) {
                var id = parseInt(sets[j]);
                html += WordSeer.model.SubsetModel
                    .makeSubsetTag(id);
            }
        }

        html += "</div>";

        // add metadata pills
        for (var i = 0; i < me.all_fields.length; i++) {
            var metafield = me.all_fields[i];
            if (!me.base_field_names.contains(metafield.name)) {
                var key = metafield.text;
                if (key.trim() == '') { key = metafield.name; }
                var value = record.get(metafield.name);
                if (value) {
                    html = html + "<div class='metatag'";
                    var onclick = 'Ext.getCmp("' + me.id + '").fireEvent("tagclicked",'
                        + 'this, Ext.getCmp("' + me.id + '"));';
                    html = html + " onclick='" + onclick + "'";
                    html = html + " metaname='" + metafield.name + "'";
                    html = html + "><span class='key'>" + key +
                        "</span><span class='value'>" + value + "</span></div>";
                }
            }
        }

        // make individual words clickable and highlight search terms
        var i = 0;
        html = html.replace(/class='word'/g,
            function(match) {
                cls = "word ";
                // *********************************
                // TODO: this highlighting code doesn't work
                // sentence.gov_index is undefined
                // *********************************
                // if (sentence.gov_index.contains(i.toString())) {
                //     // cls += "gov-highlight ";
                //     cls += ' search-highlight';
                // }
                // if (sentence.dep_index == i) {
                //     // cls += "dep-highlight ";
                //     cls += ' search-highlight';
                // }
                i += 1;
                return (' onclick="Ext.getCmp(\'' +
                    me.id +'\').fireEvent(\'wordclicked\', this, ' +
                    'Ext.getCmp(\'' + me.id +'\'));"' +
               "container-id='" +me.id+"' class='" + cls + "'");
            });
            return {
                tag: 'td',
                html: html
            };
    },
});
