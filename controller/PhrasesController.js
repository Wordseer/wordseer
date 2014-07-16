/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Controls searching for frequent phrases and filtering by frequent words and
phrases. Controls the {@link WordSeer.view.frequentwords.FrequentWordsList}
and {@link WordSeer.view.phrases.PhrasesList}
*/
Ext.define('WordSeer.controller.PhrasesController', {
	extend: 'Ext.app.Controller',
	stores: [
		'PhrasesStore',
	],
	models: [
		'PhraseModel',
	],
	views: [
		'phrases.PhrasesList',
		'frequentwords.FrequentWordsList',
	],
	init: function() {
		console.log('Phrases controller initialized');
		this.control({
			'layout-panel': {
				newSlice: this.getFrequentPhrasesForSlice
			},
			'phraseslist': {
				optionEvent: function(view, eventName, option, option_el) {
					switch (eventName) {
						case 'click':
							if (option.option.name == 'has_function_words') {
								view.has_function_words =
									!view.has_function_words;
								this.applyFilters(view);
							}
							break;
						case 'change':
							if (option.option.name == 'length') {
								view.length = option_el.getAttribute('value');
								this.applyFilters(view);
							}
					}
				},
				select: this.filterByClickedPhrase,
			},
		});
	},
	getFrequentPhrasesForSlice: function(panel, formValues) {
		if (!panel.formValues) {
			panel.formValues = formValues;
		} else {
			if (!panel.getLayoutPanelModel().isSameSlice()) {
				var params = {
					instance: getInstance()
				};
				Ext.apply(params, formValues.serialize());
				if (formValues.search && formValues.search.length > 0) {
					Ext.apply(params, formValues.search[0]);
				}
				panel.getLayoutPanelModel().getPhrasesStore().load(
					{params: params});
			}
		}
	},

	/** Asks the {@link WordSeer.store.PhrasesStore} backing the given
	{@link WordSeer.view.phrases.PhrasesList} to load the frequent phrases that
	match the given search query from the server.

	@param {WordSeer.model.FormValues} formValues A
	formValues object representing a search query.
	@param {WordSeer.view.phrases.PhrasesList} phrases_list_view The view that
	will display the data.
	@param {Function} callback The function to call after the data has been
	loaded.
	@param {Object} scope The scope in which to execute the callback.
	*/
	fetchFrequentPhrases: function(formValues, phrases_list_view) {
		var params = {
			instance: getInstance()
		};
		Ext.apply(params, formValues.serialize());
		if (formValues.search && formValues.search.length > 0) {
			Ext.apply(params, formValues.search[0]);
		}
		params['has_function_words'] = phrases_list_view.has_function_words;
		params['length'] = phrases_list_view.length;
		phrases_list_view.getStore().removeAll();
		phrases_list_view.getStore().load({
			params:params
		});
		phrases_list_view.getStore().getProxy().extraParams = params;
	},

	/** Adds a new filter by the clicked word or phrase to the parent
	{@link WordSeer.view.widget.Widget}'s {@link WordSeer.model.FormValues}.

	@param {WordSeer.view.phrases.PhrasesList
	| WordSeer.view.frequentwords.FrequentWordsList } list_view The view
	displaying the row that was clicked.

	@param {WordSeer.model.PhraseModel | WordSeer.model.WordModel} model The
	record that was clicked.
	*/
	filterByClickedPhrase: function(list_view, model) {
		var panel = list_view.up('layout-panel');
		var formValues = panel.getLayoutPanelModel().getFormValues().copy();
		formValues.phrases.push(model);
		var widget = panel.down('widget');
		if (widget) widget.setFormValues(formValues);
		panel.fireEvent('searchParamsChanged', panel, formValues);
	},

	/** Applies the "show stop words" and "group lemmas together" filters to the
	{@link WordSeer.view.phrases.PhrasesList} after data has been fetched
	from the server.

	@param {WordSeer.view.phrases.PhrasesList} phrases_list_view The view to
	which to apply the filters.
	*/
	applyFilters: function(phrases_list_view) {
		var formValues = phrases_list_view.up('layout-panel').formValues;
		this.fetchFrequentPhrases(formValues, phrases_list_view);
	}
});
