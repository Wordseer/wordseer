/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Displays a drop-down menu of the current list of word sets created by the
user. Backed by a {@link WordSeer.store.PhraseSetListStore} instance, used by the
{@link WordSeer.view.search.UniversalSearchForm}.
*/
Ext.define('WordSeer.view.search.PhraseSetComboBox',{
    extend:'Ext.form.field.ComboBox',
    alias:'widget.PhraseSetcombobox',
    initComponent:function(){
        this.store = Ext.getStore('PhraseSetListStore');
        this.typeIsWord = true;
        this.callParent(arguments);
    },
    queryMode:'local',
    valueField:'id',
    enableKeyEvents:true,
    autoSelect: false,
    selectOnFocus: true,
    emptyText:'search for...',
    value:"",
    displayField:'text',
    listConfig: {
        getInnerTpl: function() {
            var template ='<span class="combo-box-phrase-set">';
            template += '<img class="combo-box-phrase-set" src="../../style/icons/phrase-sets-window.png">';
            template += '{text}';
            template += '</span>';
            return template;
        }
    },
    listeners: {
        afterrender: function() {
            Ext.defer( function(combobox) {
                this.fireEvent('change', combobox);
            },1000, this, [this]);
        }
    },
});
