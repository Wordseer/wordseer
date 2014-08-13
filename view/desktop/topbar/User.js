/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.desktop.topbar.User', {
    extend: 'Ext.button.Button',
    alias: 'widget.user-button',
    requires:[
        'Ext.menu.Menu',
        'Ext.form.*',
    ],
    width:75,
    id:'user',
    plain:true,
    initComponent:function(){
        this.logoutMenu = Ext.create('Ext.menu.Menu', {
            align:'tr-br',
            hidden: true,
            items:[
                {
                    text: 'Sign out',
                    action: 'sign-user-out',
                }
            ]
          });
        this.setText(getUsername());
        this.callParent(arguments);
    },      
});