/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Controls searching for frequent words that match a search
query. Controls the {@link WordSeer.view.frequentwords.FrequentWordsList}.
*/
Ext.define('WordSeer.controller.FrequentWordsController', {
	extend: 'Ext.app.Controller',
	views: [
		'frequentwords.FrequentWordsList',
		'phrases.PhrasesList'
	],
	init: function() {
		this.control({
			'layout-panel': {
				'newSlice': this.getFrequentWordForSlice,
				'menuButtonClicked': function(panel, type, button) {
					if (type == 'frequent-words') {
						this.showFrequentWordsOverlay(panel, button);
					}
				}
			},
			'frequent-words, phraseslist': {
				optionEvent: function(view, eventName, option, option_el) {
					var action = option.option.action;
					if (action == 'group-by-stem') {
						view.groupedByStem = !view.groupedByStem;
						this.applyFilters(view);
					} else if (action == 'order-by-score') {
						view.orderedByDiffProp = !view.orderedByDiffProp;
						this.applySorter(view);
					}

				},
			},
			'frequent-words': {
				datachanged: this.lollipop,
				afterrender: this.lollipop,
			}
		});
	},

	/** Gets and stores the most frequent words of each part of speech in this
	slice.
	@param {WordSeer.view.windowing.viewport.LayoutPanel} panel The panel
	to which the metadata belongs.
	@param {WordSeer.model.FormValues} formValues a formValues object
	representing the search query.
	*/
	getFrequentWordForSlice: function(panel, formValues) {
		if (!panel.formValues) {
			panel.formValues = formValues;
		}
		if (!panel.getLayoutPanelModel().isSameSlice()) {
			var params = {};
			Ext.apply(params, formValues.serialize());
			var model = panel.getLayoutPanelModel();
			// make one AJAX request then filter and populate the stores
			Ext.Ajax.request({
                    method: 'GET',
                    disableCaching: false,
                    url: ws_api_path + ws_project_path + project_id +
                    '/associated_words',
                    params: params,
                    scope: this,
                    callback: function(opts, success, response){
                    	if (!success) return console.log('panel: co-ocurring words request failed');
                    	// populate the stores
				        var related_words = Ext.decode(response.responseText).Words;
				        model.NStore.add(_.where(related_words, {category: 'Nouns'}));
				        model.JStore.add(_.where(related_words, {category: 'Adjectives'}));
				        model.VStore.add(_.where(related_words, {category: 'Verbs'}));  
                    },
                });
		}
	},

	/** Applies the "group word forms together" filter to the
	{@link WordSeer.view.frequentwords.FrequentWordsList}.

	@param {WordSeer.view.frequentwords.FrequentWordsList} The view that was
	clicked.
	*/
	applyFilters: function(frequent_words_list) {
		var store = frequent_words_list.getStore();
		var value = frequent_words_list.groupedByStem? 1 : 0;
		store.clearFilter();
		store.filter({
			property: 'is_lemmatized',
			value: value,
		});
	},

	/** Applies the sorter by the score_sentences DESC field to the
	{@link WordSeer.view.frequentwords.FrequentWordsList}.
	@param {WordSeer.view.frequentwords.FrequentWordsList} The view that was
	clicked.
	*/
	applySorter: function(frequent_words_list) {
		var store = frequent_words_list.getStore();
		var property = 'count';
		if(frequent_words_list.orderedByDiffProp) {
			property = 'score_sentences';
		}
		store.sort({
			property: property,
			direction: 'DESC',
		});
	},

	/**
	Shows the frequent words overlay.
	@param {WordSeer.view.windowing.viewport.LayoutPanel} panel The layout
	panel upon which to show the overlay.

	@param {HTMLElement} button The button under which to show this overlay like
	a menu.
	*/
	showFrequentWordsOverlay: function(panel, button) {
		if (!panel.getComponent('frequent-words-overlay')) {
			var button_el = panel.getEl().down(
				'span.panel-header-menubutton.frequent-words');
			var overlay = Ext.create('WordSeer.view.menu.MenuOverlay', {
				destroyOnClose: false,
				button: button_el,
				floatParent: panel,
				itemId: 'frequent-words-overlay',
				title: "Frequent Words",
				width: 380,
				height: "75%",
				layout: 'accordion',
				draggable: true,
				items: [
					Ext.create("Ext.panel.Panel", {
						title: 'Nouns',
						items: [
							{
								xtype: 'frequent-words',
								store: panel.getLayoutPanelModel().NStore,
								pos: "Nouns"
							}
						]
					}),
					Ext.create("Ext.panel.Panel", {
						title: 'Verbs',
						items: [
							{
								xtype: 'frequent-words',
								store: panel.getLayoutPanelModel().VStore,
								pos: "Verbs"
							},
						]
					}),
					Ext.create("Ext.panel.Panel", {
						title: 'Adjectives',
						items: [
							{
								xtype: 'frequent-words',
								store: panel.getLayoutPanelModel().JStore,
								pos: "Adjectives"
							},
						]
					}),
					Ext.create("Ext.panel.Panel", {
						title: 'Phrases',
						items: [
							{
								xtype: 'phraseslist',
								store: panel.getLayoutPanelModel().getPhrasesStore()
							}
						]
					}),
				],
			});
			overlay.showBy(button_el);
			panel.add(overlay);
		}
	},

	lollipop: function(component){
		var svg = d3.select(component.el.dom)
			.selectAll('.distinct .lollipop')
			.datum(function(){ 
				// browser support for dataset on SVG is spotty, so access
				// the data attribute manually -_-
				return {score_sentences: this.getAttribute('data-score_sentences')}; 
			});

		var maxscore = d3.max(svg.data(), function(d){
			return +d.score_sentences;
		});
		var r = 4;
		var scale = d3.scale.linear()
			.domain([0, maxscore])
			.range([r, 100-r]);

		svg.append('circle')
			.attr('cx', function(d){
				return scale(+d.score_sentences);
			})
			.attr('cy', 8)
			.attr('r', r);

		svg.append('line')
			.attr('x1', scale(0))
			.attr('x2', function(d){
				return scale(+d.score_sentences); 
			})
			.attr('y1', 8)
			.attr('y2', 8)
			// .attr('stroke', '#000')
			.attr('stroke-width', 1);
	}
});
