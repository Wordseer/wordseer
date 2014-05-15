/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('Account.view.instance.InstanceManager', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.instancemanager',
	requires: [
		'Account.view.instance.List',
	],
	items: [
		{xtype: 'instancelist'},
		{
			xtype: 'button', 
			text: 'Create a new instance',
			action: 'create_instance',
		}
	]
})