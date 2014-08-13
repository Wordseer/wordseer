/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Displays the contents of a document. */
Ext.define('WordSeer.view.document.DocumentViewer', {
    extend:'Ext.Container',
    autoScroll:true,
    requires:[
        'WordSeer.view.sentence.Sentence',
        'WordSeer.view.Word',
        'WordSeer.model.WordModel',
    ],
    alias:'widget.document-viewer',
    autoScroll:true,
    initComponent: function() {
        /**
        @event wordclicked
        Fired when the user clicks a word in this document. Words are rendered
        from sentences by the
        {@link WordSeer.view.sentence.Sentence#draw draw} static method from the
        {@link WordSeer.view.setnence.Sentence Sentence} class.

        @param {HTMLElement} word The HTML span element that was clicked. The span
        has the following attributes:
            word-id: The ID of the word
            sentnce-id: the id of the sentence in which the word appears
        The text of the HTML span is the word.
        */
        this.addEvents('wordclicked', 'search');
        this.id = Ext.id();
        this.callParent(arguments);
    },

    draw:function(document_model_instance){
        this.getEl().mask('loading');
        this.data = document_model_instance.raw;
        //this.contents = this.up('panel').getComponent('contents');
        this.getEl().mask("Loading...")
        var t1 = new Date();
        this.drawDocument();
        var t2 = new Date();
//        console.log("Time to draw HTML: " +
//            ((t2.getTime() - t1.getTime())/1000)+"s");
        if (this.sentence_id) {
            this.scrollToSentence(this.sentence_id);
        }
        this.getEl().unmask();
    },

    drawDocument:function(){
        //this.up('layout-panel').setTitle(this.data.title);
        var document = this.data.units["document"][this.data.id];
        var html = new goog.string.StringBuffer();
        this.renderUnit(document, html);
        $(this.getEl().dom).html(html.toString());
    },

    renderUnit: function(unit, html){
        html.append('<div class="unit ' + unit.unit_name
            + '" unit-name="' + unit.unit_name
            + '" unit-id="' + unit.unit_id +
            + '" unit-number="' + unit.unit_number + '">');
        html.append('<div class="metadata">');
        var metadata_by_propery = {};
        for(var i = 0; i < unit.metadata.length; i++) {
            var metadata = unit.metadata[i];
            if(metadata.value_is_displayed == 1) {
                if (!metadata_by_propery[metadata.property_name]) {
                    metadata_by_propery[metadata.property_name] = []
                }
                if (metadata.value && metadata.value.length > 0) {
                    metadata_by_propery[metadata.property_name].push(
                        metadata)
                }
            }
        }
        var property_names = keys(metadata_by_propery);
        for (var i = 0; i < property_names.length; i++) {
            var property_name = property_names[i];
            var values = metadata_by_propery[property_name];
            if (values.length > 0) {
                html.append('<span class="metadata">');
                if (values[0].name_is_displayed == 1) {
                    html.append('<span class="metadata-name">');
                    html.append(values[0].name_to_display);
                    html.append(':</span>');
                }
                for (var j = 0; j < values.length; j++) {
                    var value = values[j].value;
                    html.append('<span class="metadata-value">');
                    html.append(value);
                    html.append('</span>');
                }
                html.append('</span>');
            }
        }
        html.append('</div class="metadata">');
        var children = this.data.children[unit.unit_name][unit.unit_id];
        html.append('<div class="content">')
        for(var i = 0; i < children.length; i ++){
            var child_info = children[i];
            var child_id= child_info.id;
            var child_name = child_info.name;
            var subUnit = this.data.units[child_name][child_id];
            if(subUnit.unit_name == "sentence"){
                this.renderSentence(subUnit, html);
            } else {
                this.renderUnit(subUnit, html);
            }
        }
        html.append('</div>')
        html.append('</div class="unit">');
//        console.log("drawing unit: " + unit.unit_id);
    },

    /** Adds HTML for the given sentence to the string buffer containing the
    document HTML.

    @param {Object} sentence A sentence object containing the following fields
        - words: a list of {word: id:} pairs.
    */
    renderSentence: function(sentence, html){
        var highlit = sentence.sentence_id == this.sentence_id;
        WordSeer.view.sentence.Sentence.draw(sentence, html, this.id, highlit);
    },

    /** Scrolls the sentence with the given ID into view
    @param {Number} sentence_id The ID of the sentence to scroll into view.
    */
    scrollToSentence: function(sentence_id) {
        var container = $(this.getEl().dom);
        var sentence_element = container.find(
            'span.sentence[sentence-id='+sentence_id+']');
        container.scrollTo(sentence_element.parent());
    }
})

