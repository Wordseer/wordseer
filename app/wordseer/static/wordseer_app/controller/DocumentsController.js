/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Controls views that display information about documents:
	- {@link WordSeer.view.widget.DocumentBrowserWidget}
	- {@link WordSeer.view.document.DocumentViewer}
	- {@link WordSeer.view.document.DocumentGrid}
	- {@link WordSeer.view.sentence.SentenceList}
*/
Ext.define('WordSeer.controller.DocumentsController', {
	extend:'Ext.app.Controller',
	requires: [
		'WordSeer.store.DocumentStore',
	],
	models: [
		'DocumentModel',
	],
	stores: [
		'DocumentStore',
	],
	views: [
		'widget.DocumentBrowserWidget',
		'widget.DocumentViewerWidget',
		'document.DocumentViewer',
		'document.DocumentGrid',
		'sentence.SentenceList'
	],
	init: function() {
//		console.log('Document controller initialized');
		Ext.Ajax.request({
			url: ws_api_path + 'projects/' + project_id + '/properties',
			method:'GET',
			disableCaching: false,
			params:{
				instance:getInstance(),
				unit: 'document'
			},
			scope:this,
			success:function(response){
				var data = Ext.decode(response.responseText);
				var newFields = [
					{name: 'has_text', type: 'boolean', default: false},
					'units',
					'children',
					{name:'id', type:'int'},
					'title',
					'metadata',
					{name:'matches', type:'int', sortType: 'asInt'},
					{name:'document_set', type:'string', defaultValue: '', text:'Sets'},
				];
				for (var i = 0; i < data.length; i++) {
					newFields.push({
						text: data[i].nameToDisplay?data[i].nameToDisplay:data[i].propertyName,
						name: data[i].propertyName,
						type: data[i].type == 'number'? 'float': 'auto',
						sortType: data[i].type == 'number'? 'asFloat': '',
					});
				}
				WordSeer.model.DocumentModel.setFields(newFields);
			}
		});
		//Load up the store of documents.
		this.getStore('DocumentStore').load();
		this.control({
			// Sentence list.
			'wordseer-menuitem[action=open-document]': {
				click: function(menuitem){
					var documentID = menuitem.up('wordseer-menu')
						.getDocumentId();
					var sentenceID = menuitem.up('wordseer-menu')
						.getSentenceId();
					this.openDocument(documentID, sentenceID);
				},
			},
			// Document Viewer
			'document-viewer': {
				search: this.drawDocument
			},
			'document-grid' : {
				search: this.searchForDocuments
			}
		});
	},

	/* The user has decided to open a document for viewing */
	openDocument:function(document_id, sentence_id) {
		var formValues = Ext.create('WordSeer.model.FormValues');
		Ext.apply(formValues, {
				document_id: document_id,
				sentence_id: sentence_id,
				widget_xtype: 'document-viewer-widget',
			});
		var history_item = this.getController('HistoryController')
			.newHistoryItem(formValues);
		this.getController('WindowingController')
			.playHistoryItemInNewPanel(history_item.get('id'));
	},

	/** Reads the document data in from the store and tells the document viewer
	to draw it

	@param {WordSeer.model.FormValues} formValues a
	formValues object representing a search query.
	@param document_viewer The {@link WordSeer.view.document.DocumentViewer} The
	DocumentViewer displaying this document.
	*/
	drawDocument: function(formValues, document_viewer) {
		document_viewer.sentence_id = formValues.sentence_id;
		var params = formValues.serialize();
		var param_string = JSON.stringify(params);
		var document = Ext.StoreManager
			.getByKey('DocumentStore')
			.getById(formValues.document_id);
		if (!document || !document.get('has_text') ||
				document_viewer.current_params != param_string) {
			document_viewer.current_params = param_string;
			params.include_text = "true";
			WordSeer.model.DocumentModel.load(formValues.document_id, {
				scope: document_viewer,
				params: params,
				success: function(document) {
					document_viewer.draw(document);
				}
			});
		} else {
			document_viewer.draw(document);
		}
	},

	/* Search for documents */
	searchForDocuments: function(formValues, grid){
		var params = {
			include_text: false,
		};
		Ext.apply(params, formValues.serialize());
		grid.formValues = params;
		grid.getStore().load({
			params: params,
		});
	},
});
