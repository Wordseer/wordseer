/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('Account.controller.User', {
    extend: 'Ext.app.Controller',
    views: [
    	'user.SignIn',
    	'instance.InstanceManager',
    ],
    models: [
    	'User',
    	'Instance'
    ],
    stores: [
    	'Users',
    	'Instances'
    ],
    statics: {
    	url: '../python/user.py'
    },

    /** Called before the page is rendered, sets up bindings between the
    controller and the events it responds to on the view. **/
    init: function() {
    	this.control({
    		// Controls for buttons on the sign-up/sign-in form.
    		'button[action=signin]': {
    			click: this.signIn
    		},
    		'button[action=signup]': {
    			click: this.signUp
    		},
    		'button[action=submit]': {
    			click: this.sendSignIn
    		}
    	})
    },

    /** Shows the sign up button, hides the sign in button and second password 
    field */
    signIn: function(button) {
		var form = button.up('form');
		var other = form.down('button[action=signup]');
		var type = form.down('textfield[name=type]');
		var password_field = form.down('textfield[name=password2]');
		button.hide();
		other.show();
		password_field.hide();
		type.setValue('sign-up');
   	},

   	/** Shows the sign in button and second password field, hides the 
   	sign up button. */
   	signUp: function(button) {
		var form = button.up('form');
		var other = form.down('button[action=signin]');
		var type = form.down('textfield[name=type]');
		var password_field = form.down('textfield[name=password2]');
		other.show();
		button.hide();
		password_field.show();
		type.setValue('sign-up');
	},

	/** Sends the user's username and password to the server. **/
	sendSignIn: function(button) {
		var values = button.up('form').getValues();
		Ext.Ajax.request({
			method: 'GET',
			url: this.self.url,
			params: values,
			success: this.recieveSignInResponse,
			scope: this,
		})
	},
	/** Checks to see whether the user has signed in or signed up **/
	recieveSignInResponse: function(response) {
		var data = Ext.decode(response.responseText);
		if(data.error == "no-error"){
		   	var user = new Account.model.User(data);
		   	setUsername(data.username);
		   	for (var i = 0; i < data.instances.length; i++) {
		   		this.getInstancesStore()
		   			.add(data.instances[i]);
		   	}
		   	var viewport = Ext.ComponentQuery.query('viewport')[0];
		   	viewport.add({xtype:'instancemanager'});
		   	var signIn = viewport.query('usersignin')[0];
		   	signIn.up().remove(signIn);
		 } else {
	    	signUserOut(); // util.js
			if(data.error == "already-exists"){
				alert("An account with that username already exists.");
			}else if(data.error == "wrong-password"){
				alert("You entered the wrong password.");
			}else if(data.error == "no-user"){
				alert("No such username.");
			}else if(data.error == "stranger"){
				alert("You are not on the list of authorized users, email aditi@cs.berkeley.edu for access.");
			}else if(data.error = 'no-more'){
				alert("All authorized users are already signed up. Email aditi@cs.berkeley.edu for access.");
			}else if(data.error = 'invalid-characters'){
			    alert("Either your username or your password contains invalid characters. Please try again with something different.");
			}
	    }
	}

});