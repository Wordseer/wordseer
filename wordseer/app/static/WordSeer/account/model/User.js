/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('Account.model.User', {
	extend: 'Ext.data.Model',
	fields: [
		{name:'id', type:'int'}, 
		{name:'username', type: 'string'}
	]
})