/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('Account.controller.Instances', {
    extend: 'Ext.app.Controller',
	views: [
		'instance.InstanceManager',
		'instance.create.InstanceCreationWizard',
		'instance.create.ProgressLogWatcher',
	],
	models: [
		'User', 
		'Instance',
	],
	stores: [
		'Users',
		'Instances',
	],
	statics: {
		status_url: '../python/status.py',
	},

	/** Bind controls to events triggered on the view **/
	init: function() {
		this.control({
			/* Instance list */
			'button[action=delete_instance]':{
				click: this.deleteInstance
			},
			'button[action=create_instance]':{
				click: this.createInstance
			},
			/** Instance Creation Wizard */
			'button[action=instance_creation_next]': {
				click: function(button) {
					this.navigateCreationWizard(button.up('panel'), 'next')
				}
			},
			'button[action=instance_creation_previous]': {
				click: function(button) {
					this.navigateCreationWizard(button.up('panel'), 'prev')
				}
			},
			'button[action=start_processing_instance]': {
				click: this.startProcessing
			},
		})	
	},

	/** Deletes an instance. */
	deleteInstance: function() {
		console.log('Delete button clicked!');
	},

	/** Starts the instance creation wizard if one is not already in progress.*/
	createInstance: function() {
		var in_progress = Ext.ComponentQuery.query('instancecreationwizard');
		if (in_progress.length == 0) {
			var viewport = Ext.ComponentQuery.query('viewport')[0];
			viewport.add({xtype:'instancecreationwizard'});
			var window = Ext.ComponentQuery
				.query('instancecreationwizard')[0].show();		
		}
	},

	/** Navigates between the pages of the instance creation wizard */
	navigateCreationWizard: function(panel, direction) {
		var layout = panel.getLayout();
    	layout[direction]();
   		Ext.getCmp('move-prev').setDisabled(!layout.getPrev());
   		Ext.getCmp('move-next').setDisabled(!layout.getNext());
   		Ext.getCmp('start-processing').setDisabled(layout.getNext());
	},

	/** Tells the server to start the java pipeline processing the XML data */
	startProcessing: function(button) {
		var window = button.up('window');
		var instanceId = window.getInstanceId(); 
		var viewport = Ext.ComponentQuery.query('viewport')[0];
		Ext.destroy(window);
		viewport.add({xtype:'progresslogwatcher', instanceId:instanceId});
//		console.log('Started processing');
		Ext.ComponentQuery
				.query('progresslogwatcher')[0].show()
	},

});