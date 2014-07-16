/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('Account.view.user.SignIn', {
	extend: 'Ext.form.Panel',
	alias: 'widget.usersignin',

	title: 'Sign In',
	width: '300',
	height:'500',
	bodyPadding: 10,
	// The fields.
	defaultType: 'textfield',
	items: [
		{
			fieldLabel: 'Username',
			name: 'username',
			allowBlank: false
		},
		{
			fieldLabel:'Password',
			name:'password',
			allowBlank: false,
			inputType: 'password'
		},
		{
			fieldLabel: 'Confirm password',
			name: 'password2',
			inputType: 'password',
			hidden: true
		},
		{
			name:'type',
			value: 'sign-in',
			hidden: true
		}
	],

	// Buttons for signing in, clearing the form and signing up.
	buttons: [
		{
			text:"Don't have a username? Sign up.",
			action: 'signup',
		},
		{
			text: "Already have a username? Sign in.",
			action:'signin',
			hidden: true
		},
		{
			text:'Submit',
			action:'submit',
		},
	]
})