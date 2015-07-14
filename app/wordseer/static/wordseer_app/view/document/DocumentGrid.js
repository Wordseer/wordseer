/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Displays a searchable, browsable list of all the documents in a collection.
Controlled by {@link WordSeer.controller.DocumentsController}.
*/
Ext.define('WordSeer.view.document.DocumentGrid',{
    extend:'WordSeer.view.export.ExportableTable',
    alias:'widget.document-grid',
    title: 'Documents',
    requires:[
        'WordSeer.store.DocumentStore',
        'WordSeer.view.collections.SetsToolbar',
        'WordSeer.model.DocumentModel',
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
    initComponent: function() {
        var me = this;
        this.store = Ext.create('WordSeer.store.DocumentStore');
        this.selModel = new Ext.selection.CheckboxModel({
            checkOnly: true,
        });
        /**
        @event search Fired when the user performs a new search or when a new
        instance of this view is opened. This event is handled by
        {@link WordSeer.controller.DocumentsController#searchForDocuments}.

        @param {WordSeer.model.FormValues} formValues A
        formValues object representing a search query.
        @param {WordSeer.view.document.DocumentGrid} a reference to this panel,
        the one in which the 'search' event is being fired.
        */

        /**
        @event itemdblclick Called when a document is this view is
        double-clicked. Causes the document
        @param {WordSeer.view.document.DocumentGrid} A reference to this view.
        @param {WordSeer.model.DocumentModel} record The DocumentModel for the
        document that was clicked.
        */
        this.addEvents('search');
        this.columns = [
            {
                headerTitle:'Matches',
                field:'matches',
                itemID:'matchColumn',
                width:50
            },
            {
                headerTitle: 'Sets',
                field: 'document_set',
                renderer: function(record, field) {
                    var sets = record.get(field);
                    var html = "";
                    if (sets.trim().length  > 0) {
                        var ids = sets.trim().split(" ");
                        for (var j = 0; j < ids.length; j++) {
                            html += WordSeer.model.
                                SubsetModel.makeSubsetTag(ids[j]);
                        }
                    }
                    return {html:html, tag:'td'};
                }
            }
        ];

        this.columnsLoaded = false;

        this.store.on('load', function(store, records, successful){
            // choose columns to display based on property fields returned
            if (successful && me.columnsLoaded == false) {
                me.columnsLoaded = true;
                var model = me.store.model;
                var base_field_names = model.getBaseFieldNames();
                var returned_fields = Object.keys(records[0].raw);

                for (var i = 0; i < returned_fields.length; i++) {
                    var field = returned_fields[i];
                    if (!base_field_names.contains(field)) {
                        var column_def = {
                            'headerTitle': field,
                            'field': field,
                            'flex': 1,
                        };
                        var c = Ext.create('WordSeer.model.ColumnDefinition', column_def)
                        me.columns.push(c);
                    }
                }
            }
        });
        
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
});
