/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Responds to search events on the {@link WordSeer.view.sentence.SentenceList}
*/
Ext.define('WordSeer.controller.SentenceListController', {
	extend: 'Ext.app.Controller',
	requires: [
		'WordSeer.store.SentenceSearchResultStore',
	],
	views: [
		'sentence.SentenceList',
		'widget.SentenceListWidget',
	],
	init: function() {
		this.control({
			'sentence-list': {
				/** Makes the {@link WordSeer.view.sentence.SentenceList}'s
				grid load with the passed-in form value parameters.

				@param {WordSeer.model.FormValues} formValues a formValues object
				specifying the search.

				@param {WordSeer.view.sentence.SentenceList} grid The sentence
				list in which to display the new search results.
				*/
				search: function(formValues, grid) {
					grid.getStore().load({params:formValues.serialize()});
				},
			}
		});
	}
});
