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

				}
			},
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
			var params = {
				instance: getInstance(),
				user: getUsername(),
			};
			Ext.apply(params, formValues.serialize());
			if (formValues.search && formValues.search.length > 0) {
				Ext.apply(params, formValues.search[0]);
			}
			var model = panel.getLayoutPanelModel();
			model.NStore.load({params:Ext.apply( params, {pos:'N'})});
			model.VStore.load({params:Ext.apply( params, {pos:'V'})});
			model.JStore.load({params:Ext.apply( params, {pos:'J'})});
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
				width: 1200,
				height: 410,
				items: [
					{
						xtype: 'frequent-words',
						flex:1,
						pos: 'N',
						store: panel.getLayoutPanelModel().NStore
					},
					{
						xtype: 'frequent-words',
						flex:1,
						pos: 'V',
						store: panel.getLayoutPanelModel().VStore
					},
					{
						xtype: 'frequent-words',
						flex:1,
						pos: 'J',
						store: panel.getLayoutPanelModel().JStore
					},
					{
						xtype: 'phraseslist',
						flex:1,
						store: panel.getLayoutPanelModel().getPhrasesStore(),
					}
				]
			});
			overlay.showBy(button_el);
			panel.add(overlay);
		}
	}
});
