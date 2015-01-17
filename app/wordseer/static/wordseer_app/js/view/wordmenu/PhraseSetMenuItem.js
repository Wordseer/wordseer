/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A menu option to add a word to a word set from the
{@link WordSeer.view.wordmenu.WordMenu}. **/
Ext.define('WordSeer.view.wordmenu.PhraseSetMenuItem', {
	extend: 'WordSeer.view.wordmenu.OpenPhraseSetMenuItem',
	alias: 'widget.phrasesetmenuitem',
	requires: [
		'WordSeer.model.PhraseSetModel',
	],
	action: 'add-word-to-set',
	config: {
		current: null,
	},
});
