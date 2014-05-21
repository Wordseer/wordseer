/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.user.SignIn', {
	extend: 'Ext.form.Panel',
	alias: 'widget.usersignin',
	width: '300',
	height:'500',
	bodyPadding: 10,
	// The fields.
	defaultType: 'textfield',
	items: [
		{
			fieldLabel: 'Username',
			name: 'username',
			allowBlank: false,
		},
		{
			fieldLabel:'Password',
			name:'password',
			allowBlank: false,
			inputType: 'password'
		},
		{
			fieldLabel: 'Confirm password',
			name: 'confirm',
			allowBlank: false,
			inputType: 'password',
			hidden: true
		},
		{
			name:'type',
			value: 'sign-in',
			hidden: true
		},
		{
			xtype : 'button',
			text:"Don't have a username? Sign up.",
			action: 'signup',
		},
		{
			xtype : 'button',
			text: "Already signed up?",
			action:'signin',
			hidden: true
		},
		{
			xtype : 'button',
			text:'Go',
			action:'signin-submit',
		},
	],
})