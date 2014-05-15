/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.collections.words.PhraseSet',{
	extend:'WordSeer.view.box.Overlay',
	requires:[
			'WordSeer.view.collections.words.PhraseSetTagList',
			'WordSeer.view.box.Container',
			'WordSeer.model.WordModel',
	],
	alias:'widget.phrase-set',
	constrain:true,
	resizable: true,
	draggable: {
		delegate: 'div.databox-header'
	},
	config:{
			/**
			@cfg {WordSeer.model.PhraseSetModel} record The word set that this
			window is displaying.
			*/
			record:false,
	},
	width:200,
	minWidth:200,
	height:290,
	initComponent:function(){
		this.items = [
			{
				xtype: 'phrase-set-tag-list',
				title: this.record.get('text'),
				record: this.record
			}
		];
		this.callParent(arguments);
	},
	update: function() {
		this.removeAll();
		this.add({
				xtype: 'phrase-set-tag-list',
				title: this.record.get('text'),
				record: this.record
			});
		this.draggable = true;
	}
});
