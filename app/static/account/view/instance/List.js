/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('Account.view.instance.List' ,{
    extend: 'Ext.grid.Panel',
    alias : 'widget.instancelist',
    title : 'All Instances',
    requires: [
        'Skirtle.grid.column.Component',
    ],
    width: 500,
    store: 'Instances',  // The name of the store class.
    initComponent: function() {
        this.columns = [
            {
                header: 'Name',  
                dataIndex: 'name',  
                flex: 1
            },
            {
                header: 'Creation Date', 
                dataIndex: 'creation_date_ms',
                flex: 1
            },
            {
                header: 'Status',
                dataIndex: 'in_progress',
                xtype: 'componentcolumn',
                renderer: function(in_progress, metaData, record) {
                    if (in_progress) {
                        return {
                            xtype: 'button',
                            action: 'view-status',
                            text: 'View progress',
                        }
                    } else {
                        return record.get('status');
                    }
                }
            },
            {
                header: 'Delete', 
                flex: 1,
                xtype: 'componentcolumn',
                dataIndex: 'is_new',
                renderer: function(value, metaData, record) {
                    return {
                        xtype:'button', 
                        action: 'delete_instance',
                        text: 'Delete'
                    }
                }
            }
        ];
        this.callParent(arguments);
    },
});