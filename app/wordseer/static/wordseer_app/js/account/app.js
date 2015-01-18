/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.application({
    name: 'Account',
    appFolder: 'src/js/account', 
    launch: function() {
        Ext.create('Ext.container.Viewport', {
            items: [
                {
                    xtype: 'usersignin'
                },             
            ],
        });
    },
    controllers: [
        'Instances',
        'User'
    ]
});