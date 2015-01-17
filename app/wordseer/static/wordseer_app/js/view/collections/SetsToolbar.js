/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Displayed at the top of the {@link WordSeer.view.sentence.SentenceList}
or the {@link WordSeer.view.document.DocumentGrid}, manages adding documents
or sentences to groups.
*/
Ext.define('WordSeer.view.collections.SetsToolbar', {
    extend:'Ext.toolbar.Toolbar',
    alias:'widget.collections-toolbar',
    config: {
        /**
        @cfg {String} collectionType Either 'sentence' for sentence collections
        or 'document' for document collections.
        */
        collectionType: 'sentence'
    },
    initComponent: function() {
        this.items = [
            {
                iconCls:'add-to-set',
                text:'Add to group',
                xtype: 'button',
                action: 'add-to-set-menu',
                disabled: true,
            },
            '-',
            // Remove from collection
            {
                itemId:'remove',
                xtype: 'button',
                text:'Remove from current group',
                action: 'remove',
                iconCls:'remove-from-set',
                disabled: true,
            },

        ];
        this.callParent(arguments);
    }

})
