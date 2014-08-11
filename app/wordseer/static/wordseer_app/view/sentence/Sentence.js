/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Renders a sentence based on a list of words. Creates a `<span>` containing
a {@link WordSeer.view.Word word} for each word in the sentence.
*/
Ext.define('WordSeer.view.sentence.Sentence', {
    extend:'Ext.container.Container',
    requires:[
        'WordSeer.view.Word',
        'WordSeer.model.WordModel',
        'WordSeer.view.sentence.Space'
    ],
    alias:'widget.sentence',
    autoEl:{
        tag: 'span',
        cls: 'sentence',
    },
    config:{
        /**
        @cfg {Object} words
        The words in this sentence.
            {Array[{Object{word: {String}, word_id: {Integer}}}]}
        */
        words:[],
        /**
        @cfg {Integer} sentenceID
        The ID of this sentence.
        */
        sentenceID:false,
        /**
        @cfg {Integer} documentID
        The ID of the document that this sentence belongs to.
        */
        documentID:false,
        /**
        @cfg {Array} govIndex
        Optional, default `[]`. These fields are present
        if this is a sentence in a set of search results. The indexes
        of the matching words, or matching words in the gov position (if a grammatical
        search) withing the sentence.
        */
        govIndex:[-1],

        /**
        @cfg {Number} depIndex
        Optional, default false. The index of the matching word
        in the dep position (if a grammatical search).
        */
        depIndex:-1,

        /**
        @cfg {Object} metadata
        A hierarchical tree of metadata key-value pairs that applies to this
        sentence.
        */
        metadata: {}
    },
    statics: {
        /**
        Creates an HTML string and adds it to the passed-in StringBuffer.
        The string is a `<span>` corresponding to a sentence, containing a
        sub-`<span>` element for each word in the sentence. The words fire the
        `wordclicked` event on the element with the passed-in `container_id`
        when they are clicked.

        This method is used only by the
        {@link WordSeer.view.document.DocumentViewer DocumentViewer}
        to render sentences.

        @param {Object} sentence A config object for this class, as described
        above, except that the metadta is just a list of metadata records with
        the following properties:
            - property_name
            - type
            - value
            - property_id

        @param {goog.string.StringBuffer} string_buffer The StringBuffer to
        which to write the HTML.

        @param {String} container_id The ID of the {@link Ext.Container} on
        which to fire a `wordclicked` event if a word in the sentence is clicked.

        @param {Boolean} highlit Whether or not the `highlight` class should
        be applied to this sentence.
        */
        draw: function (sentence, string_buffer, container_id, highlit) {
            var words = sentence.words;
            var metadata = sentence.metadata;
            var sets = [];
            metadata.forEach(function(info) {
                if (info.property_name == "sentence_set") {
                    sets.push(info.value);
                    var record =  Ext.getStore('SentenceSetStore')
                        .getById(parseInt(info.value));
                    var text = "";
                    if (record) {
                        text = record.get('text');
                    }
                    var color = WordSeer.model.SubsetModel
                        .colors(info.value);
                    var rgb = d3.rgb(color);
                    var representation = "rgba("+rgb.r+","+rgb.g+","+rgb.b+",0.2)";
                    var style = "background-color:"+representation +";";
                    string_buffer.append("<span "
                        + " class='sentence-set' "
                        + " setid='" +info.value +"' "
                        + " style='" + style + "' "
                        +">");
                    string_buffer.append(WordSeer.model.
                        SubsetModel.makeSubsetTag(info.value, text));
                }
            });
            var style = "style="
            var cls = highlit? "highlight":"";
            string_buffer.append('<span class="sentence ' + cls
                + '" sentence-id="' + sentence.sentence_id + '">');
             for(var i = 0; i < words.length; i++){
                var word = words[i];
                cls = "word";
                if(i == sentence.gov_index || contains(sentence.gov_index, i)){
                    cls += ' gov-highlight';
                }else if(i== sentence.dep_index) {
                    cls += ' dep-highlight';
                }
                string_buffer.append('<span class="' + cls +'" '
                    + ' onclick="Ext.getCmp(\''
                        + container_id +'\').fireEvent(\'wordclicked\', this);"'
                    + ' oncontextmenu="Ext.getCmp(\''
                        + container_id +'\').fireEvent(\'wordclicked\', this);"'
                    + 'container-id="' + container_id
                    + '" word-id="' + word.word_id
                    + '" sentence-id="' + sentence.sentence_id + '">'
                    + word.word
                    + '</span>');
                string_buffer.append(word.space_after);
            }
            string_buffer.append('</span>');
            sets.forEach(function(s) {
                string_buffer.append("</span>");
            })
        }
    },

    initComponent: function(){
        var items = [];
        var words = this.getWords();
        for(var i = 0; i < words.length; i++){
            cls = "word";
            if(i == this.getGovIndex() || contains(this.getGovIndex(), i)){
                cls += ' gov-highlight';
            }else if(i==this.getDepIndex()){
                cls += ' dep-highlight';
            }
            var word = Ext.create('WordSeer.model.WordModel', {
                word:words[i].word,
                position: i+1,
                wordID:words[i].word_id,
                sentenceID:this.getSentenceID(),
                class:cls,
            });
            items.push({
                xtype:'word',
                record: word,
            });
            var space = words[i].space_after;
            if(space.length > 0){
                items.push({xtype:'space', html:space})
            };
        }
        this.items = items;
        sentenceInfo = {
            'sentence-id':this.getSentenceID(),
            'document-id':this.getDocumentID(),
        },
        this.autoEl = Ext.apply({}, sentenceInfo, this.autoEl);
        this.callParent(arguments);
    },
})
