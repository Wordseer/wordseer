/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A menu item in the {@link WordSeer.view.wordmenu.WordMenu word menu} that
represents the option to issue a grammatical search.

@cfg {String|Integer} gov (Optional) The {String} literal word or  {Number} ID
of the {@link WordSeer.model.PhraseSetModel} in the gov position of the
grammatical relationship.

@cfg {String} govtype (Optional) The class of the gov -- either "word" or
"phrase-set".

@cfg {String|Integer} dep (Optional) The {String} literal word or the {Number}
ID of the {@link WordSeer.model.PhraseSetModel} in the dep position of the
grammatical relationship.

@cfg {String} deptype (Optional) the class of the dep -- either "word" or
"phrase-set".

@cfg {Integer} relation The ID of the {@link WordSeer.store.GrammaticalRelationsStore
grammatical relationship}.

@cfg {Integer} count The number of times this relationship occurs in the
collection.

@cfg {String} widget The xtype of the {@link WordSeer.view.widget.Widget} in
which this search should be performed.
*/
Ext.define('WordSeer.view.wordmenu.GrammaticalSearchOption', {
    extend: 'WordSeer.view.menu.MenuItem',
    alias:'widget.grammaticalsearchoption',
    config: {
        gov:false,
        dep:false,
        relation:false,
        count: 0,
        current: false,
    },
    text: '',
    action: 'grammatical-search',
    constructor: function(cfg){
        this.initConfig(cfg);
        var text = "";
        var relation_name = "";
        var relation = Ext.getStore('GrammaticalRelationsStore')
            .getById(this.relation);
        if (relation) {
            relation_name = relation.get('name');
        }

        if (this.relation === "") {
            text = this.gov+ " (" + this.count + ")";
        } else {
            text += relation? relation_name:blank;
            text += " (";
            var blank = "____";
            text += this.gov? this.gov:blank;
            text += ", ";
            text += this.dep? this.dep:blank;
            text += ") ";
            text += this.count > 0? "  "+this.count+" ":"";
        }
        this.text = text;
        this.callParent(arguments);
    }
});
