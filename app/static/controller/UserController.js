/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Manages signing in and signing out a user.
*/
Ext.define('WordSeer.controller.UserController', {
	extend: 'Ext.app.Controller',
	views: [
		'user.SignIn',
		'desktop.topbar.User',
	],
	init: function() {
		console.log('User Controller Loaded');
		this.control({
			'user-button': {
				click: function(button) {
					this.showLogoutMenu(button);
				}
			},
			'menuitem[action=sign-user-out]':{
				click: this.signOut
			},
			'button[action=signin-submit]': {
				click: this.send
			},
			'button[action=signup]': {
				click: function(button) {
					var form = button.up('form');
					form.items.getAt(2).setVisible(true);
					form.down('[name=type]').setValue('sign-up');
					button.hide();
					button.up().down('[action=signin]').show();
				}
			},
			'button[action=signin]': {
				click: function(button) {
					var form = button.up('form');
					form.items.getAt(2).setVisible(false);
					form.down('[name=type]').setValue('sign-in');
					button.hide();
					button.up().down('[action=signup]').show();
				}
			}
		});
	},

	/** Tries to sign the user in
	@param {Ext.button.Button} button The sign-in button that was clicked.
	*/
	send: function(button) {
		var values = button.up('form').getValues();
		var username = values.username.toLowerCase().replace(/\W/g, "");
		var password = values.password.toLowerCase().replace(/\W/g, "");
        var confirm = values.confirm.toLowerCase().replace(/\W/g, "");
		var type = values.type.toLowerCase();

		var password_ok = true;
		if(username.length < 3){
			password_ok = false;
		    Ext.Msg.alert({
		    	title:"Username too short",
		    	msg:"Please pick a longer username."
		    });
		}
		if(password.length < 3){
			password_ok = false;
		    Ext.Msg.alert({
		    	title:"Password too short",
		    	msg:"Please pick a longer password."
		    })
		}
		if (type == 'sign-up') {
			if (password != confirm) {
				password_ok = false;
			    Ext.Msg.alert({
			    	title:'Passwords do not match',
			    	msg:'Your password and password confirmation did not match.'
			    })
			}
		}
		if(password != values.password) {
			password_ok = false;
		    Ext.Msg.alert({
		    	title:'Invalid characters',
		    	msg:'Please only use alphanumeric characters.'
		    });
		}
		if (password_ok) {
			Ext.Ajax.request({
			  url:'../../src/php/user/user.php',
			  method:'GET',
			  params:{
			    username:username,
				password:password,
				type: type,
			    instance:getInstance()
			  },
			  scope:this,
			  success:this.processUserData
			})
		}
	},

	/** Opens up the main WordSeer application.
	*/
	signUserIn:function(){
		Ext.getStore('HistoryItemStore').getProxy().id = ('HistoryItemStore-' +
			getUsername() +"-" +getInstance());
		Ext.getStore('HistoryItemStore').load();
		var viewport = Ext.ComponentQuery.query('viewport')[0];
		viewport.removeAll();
		viewport.add({
			xtype: 'windowing-viewport'
		});
		this.setStoreUsernames();
		this.getController('WindowingController').land();
	},

	/**
	Sets the 'user' base parameter to the current username in any stores managed
	by the Ext.StoreManager.
	*/
	setStoreUsernames: function() {
		Ext.StoreManager.eachKey(function(key, store) {
			if (store.getProxy()) {
				if (store.getProxy().setExtraParam) {
					store.getProxy().setExtraParam('user', getUsername());
				}
				store.load();
			}
		});
	},

	/** Check if a user is signed in
	*/
	isSignedIn: function(){
		if (typeof(sessionStorage) == 'undefined' ) {
			Ext.Msg.alert('Your browser does not support this feature, try upgrading.');
		} else if(sessionStorage["username"]) {
	    return true;
		}
		return false;
	},

	/** Signs a user out, removes all the items from the view,
	and displays the main sign in screen.
	*/
	signOut: function(){
		signUserOut();  // in util.js
		var viewport = Ext.ComponentQuery.query('viewport')[0];
		viewport.removeAll();
		viewport.add({
			xtype: 'usersignin',
		})
	},

	/** Displays the log-out menu next to the top bar button.
	@param {WordSeer.view.desktop.topbar.User} button The sign-out button that
	was clicked.
	*/
	showLogoutMenu: function(button){
	  button.logoutMenu.showBy(button);
	},

	/** Checks if the sign in or sign up has been successful based on the
	response from the server.
	@param {XMLHTTPResponse} response The server's response from
	src/php/user/user.php.
	*/
    processUserData:function(response){
      console.log(response);
        data = Ext.decode(response.responseText);
    	if(data.error == "no-error"){
    		setUsername(data.username)  // in util.js
        	this.signUserIn();
    	} else{
    		if(data.error == "already-exists"){
    			Ext.Msg.alert({title:"Signup failed", msg:"an account with that username already exists."});
    		}else if(data.error == "wrong-password"){
    			Ext.Msg.alert({title:'Sign in failed', msg:"You entered the wrong password."});
    		}else if(data.error == "no-user"){
    			Ext.Msg.alert({title:"Sign in failed", msg:" no such username."});
    		}else if(data.error == "stranger"){
    			Ext.Msg.alert({title:'Sign in failed', msg:"You are not on the list of authorized users, email aditi@cs.berkeley.edu for access."});
    		}else if(data.error = 'no-more'){
    			Ext.Msg.alert({title:"Sign in failed", msg:"All authorized users are already signed up. Email aditi@cs.berkeley.edu for access."});
    		}else if(data.error = 'invalid-characters'){
    		    Ext.Msg.alert({title:"Invalid characters", msg:"Either your username or your password contains invalid characters. Please try again with something different."});
    		}
    	}
    }
});
