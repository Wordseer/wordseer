/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A {@link WordSeer.view.wordmenu.WordMenu word menu} item that displays
a grammatical search option menu next to the word in the case of phrases
*/
Ext.define('WordSeer.view.autosuggest.PhrasesAutoSuggestMenuItem', {
	extend: 'WordSeer.view.autosuggest.AutoSuggestMenuItem',
	alias: 'widget.phrases-autosuggest-menuitem',
	requires: [
		'WordSeer.view.autosuggest.GrammaticalPhrasesOverlay'
	]
});
