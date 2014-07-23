/** controls dispatch of url history tokens to/from the windowing controller
*/
Ext.define('WordSeer.controller.UrlHistoryController', {
    extend: 'Ext.app.Controller',

    dispatch: function(token){
        console.log(token);
        switch (token) {
            case 'usersignin':
                Ext.create('Ext.container.Viewport', {
                    layout: 'fit',
                    items:{
                            xtype: 'usersignin',
                    }
                });
                break;
            
        }
    }
});

/* what this controller needs to do:
    decode the hash
    pass instructions to the windowing controller

*/
