/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('Account.view.instance.create.InstanceCreationWizard', {
	extend: 'Ext.window.Window',
	alias: 'widget.instancecreationwizard',
	id: 'instancecreationwizard',
	modal: true,
	width: 600,
	height:500,
	layout: 'card',
	title: 'Create a New WordSeer Instance',
	activeItem: 0,
	config: {
		instanceId: false,
	},
	bbar: [
		{
			text: 'Previous',
			id:'move-prev',
			action: 'instance_creation_previous',
			disabled: true,
		},
		{
			text: 'Next',
			id: 'move-next',
			action: 'instance_creation_next',
		},
		{
			text: 'Start Processing',
			id: 'start-processing',
			action:'start_processing_instance',
			disabled:true,
		}
	],
	items: [
		{
			html: 'Step 1',
		},
		{
			html: 'Step 2',
		},
		{
			html: 'Step 3',
		}
	]
})