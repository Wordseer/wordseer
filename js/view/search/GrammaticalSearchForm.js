/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A form for issuing grammatical search and keyword search queries.
{@img search/grammatical-search-form.png}.
*/
Ext.define('WordSeer.view.search.GrammaticalSearchForm',{
    extend:'Ext.form.Panel',
    alias: 'widget.grammatical-search-form',
    requires:[
        'WordSeer.store.DocumentSetListStore',
        'WordSeer.store.GrammaticalRelationsStore',
        'WordSeer.view.search.DocumentSetsComboBox',
        'WordSeer.view.search.PhraseSetComboBox',
        'WordSeer.view.search.GrammaticalRelationsComboBox',
        'WordSeer.view.autosuggest.PhrasesAutoSuggest'
    ],
    height: 24,
    layout: 'hbox',
    items: [
        {
            name:'gov',
            flex:1,
            //xtype:'PhraseSetcombobox',
            xtype: 'phrases-autosuggest',
        },
        {
            name:'relation',
            flex:1,
            value:"",
            xtype:'grammaticalrelationscombobox',
        },
        {
            name:'dep',
            flex:1,
            xtype:'PhraseSetcombobox',
            hidden: true,
        },
        {
            name: 'all_word_forms',
            fieldLabel: 'with stemming',
            labelAlign: 'right',
            labelWidth: 85,
            xtype: 'checkbox',
            value: 'off',
        },
        //dealing with word sets
        {
            xtype:'textfield',
            name:'govtype',
            value:'word',
            hidden:true,
        },
        {
            xtype:'textfield',
            name:'deptype',
            value:'word',
            hidden:true,
        },
        {
            xtype: 'combobox',
            name: 'target',
            value: 'new',
            valueField: 'target',
            displayField: 'text',
            store: {
                fields: ['target', 'text'],
                data: [{target: 'new', text: 'in new tab'},
                {target:'same', text: 'in current tab'}
                ]
            }
        },
        {
            xtype: 'button',
            text:'Go',
            action: 'search',
            id: 'universal-search-button',
            disabled:true,
        },
    ],

    initComponent:function(){
        if(!COLLECTIONS_LIST_STORE){
        COLLECTIONS_LIST_STORE = Ext.create(
            'WordSeer.store.DocumentSetListStore');
        }
        //if(!SENTENCE_COLLECTIONS_LIST_STORE){
            SENTENCE_COLLECTIONS_LIST_STORE = Ext.create(
                'WordSeer.store.SentenceSetListStore');
        //}
        this.callParent(arguments);
    },


})
