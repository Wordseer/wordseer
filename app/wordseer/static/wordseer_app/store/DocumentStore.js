/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.store.DocumentStore', {
	extend:'Ext.data.Store',
	model:'WordSeer.model.DocumentModel',
	proxy: {
		type:'ajax',
		noCache: false,
		url: ws_api_path + ws_project_path + project_id + '/documents/',
		reader: {
			type: 'json',
			root: 'results',
		},
		extraParams: {
	        include_text: false,
	    },
	},
})
