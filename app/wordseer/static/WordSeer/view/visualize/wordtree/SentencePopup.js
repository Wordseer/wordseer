/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Displays a pop-up showing contextual information for a sentence or sentences
in a
{@link WordSeer.view.visualize.wordtree.WordTree} or
{@link WordSeer.view.visualize.columnvis.ColumnVis}. Controlled by the
{@link WordSeer.controller.SentencePopupController}.
*/
Ext.define('WordSeer.view.visualize.wordtree.SentencePopup', {
	extend: 'Ext.window.Window',
	alias: 'widget.sentence-popup',
	requires: [
		'WordSeer.view.sentence.Sentence',
	],
	width: 200,
	maxHeight: 300,
	autoScroll: true,
	constrain: true,
	header: false,
	config: {
		/** @cfg {Array} sentences A list of
		{@link WordSeer.view.sentence.Sentence} config objects to display.
		*/
		sentences: [],

		/** @cfg {Array} metadata A list of key-value metadata pairs, any
		additional metadata for these sentences.*/
		metadata: [],
	},
	initComponent: function() {
		var items = [];
		for (var i = 0; i < this.getSentences().length; i++){
			var sentence = this.getSentences()[i];
			sentence.xtype = 'sentence';
			var meta = sentence.metadata;
			var metadata = [];
			var set_tags = "";
			if (meta) {
				keys(meta).forEach(function(property){
					var children = meta[property].children;
					children.forEach(function(child){
						var metadata_html = ('<span class="propertyname">' +
							child.propertyName +
							'</span>: <span class="propertyvalue">' + child.text +
							'</span>');
						if (child.propertyName == "sentence_set") {
							var sets = child.value+"";
							if (sets.trim().length  > 0) {
							    var ids = sets.trim().split(" ");
							    for (var j = 0; j < ids.length; j++) {
							        set_tags += WordSeer.model.
							            SubsetModel.makeSubsetTag(ids[j]);
							    }
							}
						}
						metadata.push(
						     {
						         xtype:'box',
						         cls:'metadata-facet',
						         html: metadata_html,
						     }
						 );
					})
				});
			};
			var this_sentence_items =  [
				sentence,
				{
					xtype:'component',
					autoEl:'span',
					cls:'metadata',
					html: set_tags,
				},
				{
				    xtype:'container',
				    autoEl:'span',
				    cls:'metadata',
				    items: metadata,
				},
				{
					xtype:'button',
					text: 'Go to text',
					action: 'opentext',
					index: i,
				},
			];
			this_sentence_items.forEach(function(item) {
				items.push(item);
			})
		}
		this.items = [{
			xtype: 'panel',
			layout: {
				type: 'vbox',
				align: 'stretch',
			},
			items: items
		}];

		/**
		@event mouseenter Fired when the user mouses over this window.
		@param {WordSeer.view.visualize.wordtree.SentencePopup} popup The popup
		window.
		*/
		/**
		@event mouseleave Fired when the mouse leaves this window.
		@param {WordSeer.view.visualize.wordtree.SentencePopup} popup The popup
		window.
		*/
		this.addEvents('mouseenter', 'mouseleave');
		this.callParent(arguments);
	},

	listeners: {
	  afterrender: function() {
	    var me = this;
	    me.getEl().on('mouseenter', function(){
	      me.fireEvent('mouseenter', me);
	    });
	    me.getEl().on('mouseleave', function(){
	      me.fireEvent('mouseleave', me);
	    })
	  }
	},

});
