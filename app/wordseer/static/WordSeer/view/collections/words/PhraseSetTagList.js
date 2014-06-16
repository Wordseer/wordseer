/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
Ext.define('WordSeer.view.collections.words.PhraseSetTagList',{
	extend:'WordSeer.view.overview.TagListOverview',
	alias:'widget.phrase-set-tag-list',
	requires: [
		'WordSeer.model.WordModel'
	],
	constrain:true,
	options : [
		{
			option: {
				tag: 'span',
				cls: 'button',
				html: 'Edit',
				action: 'edit-phrase-set'
			},
			listeners: [
				{
					event: 'click'
				}
			]
		},
		{
			option: {
				tag: 'span',
				cls: 'button',
				html: 'Delete this set',
				action: 'delete-phrase-set'
			},
			listeners: [
				{
					event: 'click'
				}
			]
		}
	],
	tagField: 'word',
	maxLength: 100,
	config:{
			/**
			@cfg {WordSeer.model.PhraseSetModel} record The word set that this
			window is displaying.
			*/
			record:false,
	},
	initComponent: function() {
		var data = this.record.get('phrases').map(function(phrase) {
			return {word: phrase, class:'word'};
		});
		this.store = Ext.create('Ext.data.Store', {
			model: 'WordSeer.model.WordModel',
			data: data
		});
	}

});
