/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Controls adding, removing, and updating Word Sets:
	- {@link WordSeer.view.wordmenu.WordMenu}
	- {@link WordSeer.view.collections.words.PhraseSetCanvas}
	- {@link WordSeer.view.collections.words.PhraseSetList}
	- {@link WordSeer.view.collections.words.PhraseSet}
	- {@link WordSeer.view.collections.words.PhraseSetsPanel}
	- {@link WordSeer.view.collections.words.PhraseSetWord}
The data for the word sets is stored in one master store: the
	{@link WordSeer.store.PhraseSetListStore}
*/
Ext.define('WordSeer.controller.PhraseSetsController', {
	extend: 'WordSeer.controller.SetsController',
	views: [
		'collections.words.PhraseSet',
		'wordmenu.WordMenu',
	],
	stores: [
		'PhraseSetStore',
		'PhraseSetListStore',
	],
	models: [
		'PhraseSetModel',
	],
	init: function() {
		this.control({
			'phrase-set-tag-list': {
				optionEvent: function(view, event,  option, option_el) {
					var action = option.option.action;
					if (event == 'click') {
						if (action == 'edit-phrase-set') {
							this.editPhraseSetContents(view, option, option_el);
						} else if (action  == 'delete-phrase-set') {
							this.deletePhraseSet(view, option, option_el);
						}
					}
				}
			},
			'phrase-set > header': {
				dblclick: this.startRenamePhraseSet,
				click: this.startRenamePhraseSet,
			},
			'phrase-set > header > textfield': {
				blur: this.finishRenamePhraseSet,
				specialkey: this.finishRenamePhraseSet,
			},
			'button[action=editPhraseSet]': {
				click: this.editPhraseSet,
			},
			'button[action=canceleditPhraseSet]': {
				click: this.cancelEditPhraseSet,
			},
			'set-menuitem[action="open"]': {
				click: this.openPhraseSet,
			}
		});
	},


	/** Called when the user edits the name of a word set.

	@param {Ext.grid.plugin.Editing} editor
	@param {Object} edited An edit event with the following properties:
		- grid - The grid
		- record - The record that was edited
		- field - The field name that was edited
		- value - The value being set
		- row - The grid table row
		- column - The grid Column defining the column that was edited.
		- rowIdx - The row index that was edited
		- colIdx - The column index that was edited
		- originalValue - The original value for the field, before the edit (only when using CellEditing)
		- originalValues - The original values for the field, before the edit (only when using RowEditing)
		- newValues - The new values being set (only when using RowEditing)
		- view - The grid view (only when using RowEditing)
		- store - The grid store (only when using RowEditing)
	*/
	edited: function(record) {
		var canvas = Ext.ComponentQuery.query('PhraseSetcanvas');
		if (canvas.length > 0) {
			canvas = canvas[0];
			if (canvas) {
				var PhraseSet = canvas.getPhraseSetWindow(record.get('id'));
				if (PhraseSet !== undefined) {
					PhraseSet.update();
				}
			}
		}
	},

	/** Called when the user clicks the "OK" button after manually editing the
	contents of a word set in a {@link WordSeer.view.collections.word.PhraseSet}.
	@param {Ext.button.Button} button The button that was clicked.
	*/
	editPhraseSet: function(button) {
		var phrase_set = button.up('phrase-set');
		var record = phrase_set.getRecord();
		phrase_set.getEl().mask("Marking sentences that match this set...");
		var new_values = button.up('wordseer-container').down('textarea').getValue();
		var new_name = button.up('wordseer-container').down('textfield').getValue();

		record.updatePhraseSetValues(new_values,
			function(){
				if (new_name != record.get('text')) {
					record.rename(new_name, function(){
						phrase_set.getEl().unmask();
						phrase_set.update();
						Ext.getStore('PhraseSetStore').load();
						this.getController('MetadataController').subsetsChanged();

					}, this);
				} else {
					phrase_set.getEl().unmask();
					phrase_set.update();
					Ext.getStore('PhraseSetStore').load();
					this.getController('MetadataController').subsetsChanged();
				}
			}, this);
	},

	deletePhraseSet: function(button) {
		var phrase_set_window = button.up('phrase-set');
		var record = phrase_set_window.getRecord();
		if (record) {
			record.delete(function() {
				phrase_set_window.close();
				Ext.getStore('PhraseSetStore')
					.load();
				this.getController('MetadataController').subsetsChanged();
			}, this);
		}
	},

	/** Called when the user double clicks inside the wor set window. Creates
	a textarea with the words in the set already loaded into it.
	@param {Ext.panel.Panel} canvas The interior panel in the word set window
	that was clicked on.
	*/
	editPhraseSetContents: function(view, option, option_el){
		var phrase_set_window = view.up('phrase-set');
		phrase_set_window.draggable = false;
		var phrases = phrase_set_window.getRecord().get('phrases');
		phrase_set_window.removeAll();
		phrase_set_window.add({
			xtype:'wordseer-container',
			title: 'Edit Set',
			layout:  {
				type: 'vbox',
				align: 'stretch'
			},
			items:[
				{
					xtype: 'textfield',
					name: 'title',
					itemId: 'title',
					allowblank: false,
					value: phrase_set_window.getRecord().get('text')
				},
				{
					xtype:'textarea',
					name:'words',
					label: 'Enter comma-separated words or phrases',
					height: 150,
					itemId:'word-entry',
					allowblank:false,
					value: phrases.join(", ")

				},
				{
					xtype:'button',
					itemId:'cancel-button',
					text:'Cancel',
					action: 'canceleditPhraseSet'
				},
				{
					xtype:'button',
					text:'OK',
					itemId:'ok-button',
					action: 'editPhraseSet',
				}
			],
		});
		phrase_set_window.down('textarea').focus();
	},

	/** Called when the user presses the cancel button while editing a word set.
	Discards the edits they made by simply updating the word set's view.
	*/
	cancelEditPhraseSet: function(button) {
		var phrase_set = button.up('phrase-set');
		phrase_set.update();
	},



	/** Called when the user presses enter while editing the header of a
	{@link WordSeer.view.collections.words.PhraseSet word set window}.
	@param {Ext.form.field.TextField} textfield The textfield that was edited.
	*/
	finishRenamePhraseSet: function(textfield, event) {
		if (event.getKey() == event.ENTER) {
			var new_name = textfield.getValue();
			var record = textfield.up('phrase-set').getRecord();
			if (record) {
					record.rename(new_name, function(){
						Ext.getStore('PhraseSetStore')
							.load();
						var header = this.up('header');
						header.remove(this);
						header.is_being_renamed = false;
						var record = header.up('phrase-set').getRecord();
						header.setTitle(record.get('text'));
					}, textfield);
			}
		} else if (event.getKey() == event.ESC) {
			var header = textfield.up('header');
			header.remove(textfield);
			header.is_being_renamed = false;
			header.setTitle(header.old_name);
		}
	},

	/** Called when the user right clicks inside the word sets editor.
	*/
	PhraseSetCanvasContextMenu: function(e) {
		var me = this;
		var menu = Ext.create('Ext.menu.Menu',{
			items:[
				{
					text:'New Word Set',
					iconCls:'new-set',
					action: 'new-phrase-set'
				}
			]
		});
		menu.showAt(e.getXY());
		e.preventDefault();
	},

	/** Reloads the data in the word set list store and in all the word set
	comboboxes.
	*/
	refreshPhraseSetList: function() {
		Ext.getStore('PhraseSetStore').load();
	},

	// Word menu functionality.

	/** Called when the user clicks the "add to set" button on a word menu item
	representing a word set.
	@param {Ext.menu.Item} menuitem The menuitem that was clicked.
	*/
	addToPhraseSet: function(menuitem) {
		var me = this;
		var word = menuitem.getCurrent().get('word');
		if (menuitem.getCreateNew()) { // Add to new word set.
			Ext.getStore('PhraseSetStore').getRootNode().newSet(
				function(operation) {
					var data = Ext.decode(operation.response.responseText);
					var id = parseInt(data.id);
					WordSeer.model.PhraseSetModel.load(id, {
						scope: me,
						success: function(record) {
							record.addWords(word, function(){
								Ext.getStore('PhraseSetStore').load();
								me.getController('MetadataController')
									.subsetsChanged();
							}, me);
						}
					});
				},
				menuitem, "{"+menuitem.getCurrent().get('word')+"}");
		} else {
			var record = menuitem.getPhraseSet();
			var word = menuitem.getCurrent().get('word');
			record.addWords(word, function(){
//				console.log("loading word set store after adding");
				this.refreshPhraseSetList();
				this.getController('MetadataController').subsetsChanged();
			}, this)
		}
	},

	/** Opens up the word set corresponding to the menu item.
	@param {WordSeer.view.wordmenu.SetMenuItem} button The
	{@link WordSeer.view.wordmenu.WordMenu} button that the user clicked, with
	the name of the word set to open.

	@param {Ext.EventObject} event The event object representing the button
	click event.
	*/
	openPhraseSet: function(button, event) {
		this.position = event.getXY();
		var record = button.getRecord();
		this.openPhraseSetWindow(record, event.getXY());
	},

	/** Opens the word set corresponding to the given word set record.
	If a PhraseSet widget is already open, opens the word set in that window.
	Otherwise opens the word set in a small
	{@link WordSeer.view.collections.words.PhraseSet PhraseSet window} by itself.

	@param {Number} record_id The id of the word set to open.
	@param {Array[Number]} position The x-y position of the window (x = first
	element, y = second element).
	*/
	openPhraseSetWindow: function(record, position) {
		if (!position) {
			var total_x = document.width -150;
			var total_y = document.height -150;
			var x = total_x * Math.random();
			var y = total_y * Math.random();
			position = [x, y];
		}
		var window_id = "phrase-set-window-" +record.get('id');
		var win = null;
		if (Ext.getCmp(window_id) === undefined) {
			win = Ext.create(
				'WordSeer.view.collections.words.PhraseSet', {
					id: window_id,
					record: record,
			});
			win.showAt(position[0], position[1]);
		} else {
			win = Ext.getCmp(window_id);
			win.setRecord(record);
			win.update();
		}
	}
});
