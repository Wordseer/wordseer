/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** The skeleton for the Word Frequency graph views.
*/
Ext.define('WordSeer.view.visualize.wordfrequencies.WordFrequencies', {
	extend:'Ext.Container',
	layout: 'fit',
	alias:'widget.word-frequencies',
	autoScroll: false,
	items: [
		{
			xtype: 'component',
			itemId: 'panel-header',
			html: '\
				<div class="databox-header">\
					<h2 class="databox-header">Metadata Profile</h2>\
					<div class="controls">PROPERTIES:</div>\
					<div class="display">DISPLAY AS:</div>\
				</div>',
			cls: 'panel-header'
		}, {
			xtype: 'component',
			itemId: 'canvas',
			cls: 'canvas'
		}
	],

	/** @property {Array} charts The word frequency chart objects belonging to this
	view.
	*/
	charts: [],

	/**
	@property {Array} chart_divs The word frequency chart views belonging to this
	view.
	*/
	chart_divs: [],

	/** @property {Array} As list of lists of search results matching a search query.
	*/
	data: [],

	/** @property {String} [top_n="all"] How many string facet values to show.
	*/
	top_n: 'all',

	initComponent:function(){
		/**
		@event search Fired when the user issues a search query or when the tree
		is loaded for the first time.
		@param {WordSeer.model.FormValues} formValues a
		formValues object representing a search query.
		@param {WordSeer.view.visualize.wordfrequencies.WordFrequencies} this view.
		*/
		/**
		@event draw Fired when a request for data from the server
		returns successfully.
		@param {WordSeer.view.visualize.wordfrequencies.WordFrequencies} this view.
		@param {Object} data An object containing one list of sentence records
		for each search that was issued.
		*/

		/**
		@event rendered Fired when the Controller is done drawing d3 content
		*/

		/**
		@event changeDateDetail Fired when user changes the dropdown in a chart
		with date granularity selection
		*/
		this.addEvents('search', 'change', 'rendered', 'changeDateDetail');
		this.callParent(arguments);
	}
});
