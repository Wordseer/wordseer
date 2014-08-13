/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Represents a word, word set, or grammatical relation with varying degrees of
precision. Used to hold information to convey to a
{@link WordSeer.view.wordmenu.WordMenu}.

@cfg {String} class ["word", "phrase-set", "grammatical"] The kind of item being
represented. A {@link WordSeer.view.wordmenu.WordMenu word menu} uses this field
to decide which options to show.

@cfg {String|Integer} word (Optional) If representing a word,the word to
represent or, if representing a {@link WordSeer.model.PhraseSetModel word set),
the ID of the word set.

@cfg {String|Integer} lemma (Optional) If representing a word,the lemma or root
word of the word.

@cfg {Integer} wordID  (Optional) Only used when representing a word. The ID of
the word (if known) otherwise, this instance represents the surface form of the
word, and not a specific part of speech variant of that surface form. For
example, an instance with {word: 'can'} and no ID specified would match all
instances of the word "can". However, if the ID of the noun form of "can" was
specified, the word would only match those instances of the word "can" that had
the correct ID as well (in this case, the noun "can") and leave out the others
(the verb "can").

@cfg {Integer} sentenceID (Optional) The ID of the sentence in which this word
appears (if known).

@cfg {String|Integer} gov (Optional) The {String} literal word or  {Number} ID
of the {@link WordSeer.model.PhraseSetModel} in the gov position of the
grammatical relationship.

@cfg {String} govtype (Optional) The class of the gov -- either "word" or
"phrase-set".

@cfg {String|Integer} dep (Optional) The {String} literal word or the {Number}
ID of the {@link WordSeer.model.PhraseSetModel} in the dep position of the
grammatical relationship.

@cfg {String} deptype (Optional) the class of the dep -- either "word" or
"phrase-set".

@cfg {String} relation (Required if representing a grammatical
relationship). The ID of the {@link WordSeer.store.GrammaticalRelationsStore
grammatical relationship}.

@cfg {Integer} count The number of times the item represented by this instance
occurs.

@cfg {Integer} document_count The number of times the item represented by this
instance occurs.

@cfg {Integer} lemmatized_count The number of times the lemma of this word
occurs.

@cfg {Integer} is_lemmatized 0 or 1 -- 1 if this WordModel represents the
root word, 0 if it represents a particular word form.

@cfg {String} phrase_set The space-separated list of word set ID's to which this
word belongs.
*/
Ext.define('WordSeer.model.WordModel', {
	extend:'Ext.data.Model',
	fields: [
		{name:'word', type:'string', defaultValue: ''},
		{name:'lemma', type:'string', defaultValue: ''},
		{name:'wordID', type:'int', defaultValue: -1 },
		{name:'class', type: 'string', defaultValue: 'word'},
		{name:'sentenceID', type: 'int', defaultValue: -1},
		{name: 'gov', type: 'string', defaultValue: false},
		{name: 'govtype', type: 'string', defaultValue: 'word'},
		{name: 'dep', type: 'string', defaultValue: false},
		{name: 'deptype', type: 'string', defaultValue: 'word'},
		{name: 'relation', type: 'string', defaultValue:false},
		{name: 'count', type: 'int', defaultValue: 0},
		{name: 'document_count', type: 'int', defaultValue: 0},
		{name: 'lemmatized_count', type: 'int', defaultValue: 0},
		{name: 'score_sentences', type: 'float', defaultValue: 0.0},
		{name: 'score_documents', type: 'float', defaultValue: 0.0},
		{name: 'is_lemmatized', type: 'int', defaultValue: 0},
		{name: 'id', type: 'auto'},
		{name: 'phrase_set', type:'string', defaultValue:''},
		{name:'position', type:'int', defaultValue: 0},
	],

	/**
	Returns the value of class.
	*/
	getClass: function() {
		return this.get('class');
	}
});
