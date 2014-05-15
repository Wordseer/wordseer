/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('Account.model.Instance', {
	extend: 'Ext.data.Model',
	fields: [
		{name:'id', type:'int'},
		{name: 'user_id', type: 'string'},
		{name:'name', type:'string'},
		{name:'creation_date_ms', type:'date', dateFormat:'time'},
		{name: 'status', type:'string'},
		{name:'in_progress', type:'boolean', defaultValue:false},
	]
})