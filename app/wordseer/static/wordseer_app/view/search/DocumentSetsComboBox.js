/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.search.DocumentSetsComboBox',{
    extend:'Ext.form.field.ComboBox',
    alias:'widget.collections-combobox',
    requires: [
        'WordSeer.store.DocumentSetListStore',
    ],
    queryMode:'local',
    valueField:'text',
    value:"all",
    displayField:'text',
    editable:false,
    listConfig: {
        getInnerTpl: function() {
            var template ='<span class="combo-box-collection">';
            template += '<img class="combo-box-collections" src="../../style/icons/document-browser-16.png">';
            template += '{text}';
            template += '</span>';
            return template;
        }
    },
    initComponent: function() {
        this.store = Ext.create('WordSeer.store.DocumentSetListStore');
        this.callParent(arguments);
    }
})
