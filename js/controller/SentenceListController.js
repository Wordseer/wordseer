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
		'sentence.SentenceTable',
		'widget.SentenceTableWidget',
	],
	init: function() {
		this.control({
			'sentence-list, sentence-table': {
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
				datachanged: function(widget) {
					// highlight all the words
					color_index = 0;
					colors = COLOR_SCALE; // in util.js
					var words = widget.getEl().query('.word.search-highlight');
					if (words.length > 0) {
						for (var i=0; i < words.length; i++){
							words[i].style.backgroundColor = colors[color_index];
						}
						color_index = colorLoop(color_index);
					}
					words = widget.getEl().query('.word:not(.search-highlight)');
					if (words.length > 0) {
						var formValues = widget.up('layout-panel').formValues;
						phrase_ids = []
						for (var i=0; i<formValues.phrases.length; i++){
							// get phrase IDs, split on . characters, add to phrase ids
							phrase_ids.push(formValues.phrases[i].internalId.split("."));
						}

						// check words for ID matches and color as necessary
						for (var i=0; i < words.length; i++){
							for (var x=0; x<phrase_ids.length; x++) {
								phrases = phrase_ids[x];
								for (var y=0; y<phrases.length; y++){
									var query_match = phrases.indexOf(
										words[i].getAttribute("word-id"));
									if (query_match >= 0) {
										words[i].style.backgroundColor =
										   colors[x + color_index];
									}
								}
							}
						}
					}
				}
			}
		});
	}
});
