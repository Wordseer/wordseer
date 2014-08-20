/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A list of sentences **/
Ext.define('WordSeer.view.sentence.SentenceTable',{
    extend:'WordSeer.view.export.ExportableTable',
    alias:'widget.sentence-table',
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
                html: 'Add to group',
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
                html: 'Remove from group',
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
        this.addEvents('search', 'wordclicked');

        this.columns = [
            {
                headerTitle:'Sentence',
                field:'sentence',
                cls:'word-wrap',
                flex:5,
                renderer: this.renderSentence
            }
        ];

        var model = this.getStore().model;
        var base_field_names = model.getBaseFieldNames();
        var all_fields = model.getFields();
        for (var i = 0; i < all_fields.length; i++) {
            var field = all_fields[i];
            if (!base_field_names.contains(field.name)) {
                this.columns.push({
                    headerTitle: field.text.length > 0 ? field.text: field.name,
                    field: field.name,
                    flex: 1,
                });
            }
        }
        this.callParent(arguments);

    },

    populate: function() {
        var title = 'Search Results';
        if (this.getStore().getCount() > 0) {
            title +=  " (" + this.getStore().getCount() +")";
        }
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
        var html = sentence.words;
        var me = view;
        if (html && html.length > 0) {
            var sentence_sets = record.get('sentence_set');
            if (sentence_sets && sentence_sets.trim().length > 0) {
                var sets = sentence_sets.trim().split(" ");
                for (var j = 0; j < sets.length; j++) {
                    var id = parseInt(sets[j]);
                    html += WordSeer.model.SubsetModel
                        .makeSubsetTag(id);
                }
            }
            var i = 0;
            html = html.replace(/class='word'/g,
                function(match) {
                    cls = "word ";
                    if (sentence.gov_index.contains(i.toString())) {
                        // cls += "gov-highlight ";
                        cls += ' search-highlight';
                    }
                    if (sentence.dep_index == i) {
                        // cls += "dep-highlight ";
                        cls += ' search-highlight';
                    }
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
        } else {
            return null;
        }
    },
    // listeners: {
    //     afterrender: function( eOpts ) {
    //         view = this.getView();
    //         view.tip = Ext.create('Ext.tip.ToolTip', {
    //             target: view.el,
    //             delegate: view.itemSelector,
    //             trackMouse: true,
    //             renderTo: Ext.getBody(),
    //             listeners: {
    //                 beforeshow: function updateTipBody(tip) {
    //                     tip.update(
    //                         "Double click to see this sentence in context.");
    //                 }
    //             }
    //         });
    //     }
    // }
});
