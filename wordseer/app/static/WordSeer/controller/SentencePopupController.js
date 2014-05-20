/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.controller.SentencePopupController', {
	extend: 'Ext.app.Controller',
	views: [
		'visualize.wordtree.SentencePopup',
	],
	init: function() {
		console.log('SentencePopup Controller initialized');
		this.control({
			'sentence-popup': {
				'mouseenter': this.sentencePopupMouseEnter,
				'mouseleave': this.sentencePopupMouseOut
			},
			'sentence-popup > panel > button[action=opentext]': {
				'click': this.sentencePopupGoToText
			}
		})
	},
	/** Destroys the sentence popup that appeared when a user last hovered
	a node.
	@param {WordSeer.view.visualize.wordtree.SentencePopup} popup The sentence
	popup.
	*/
	removePopup: function(popup) {
	    if (popup) {
	    	if (!popup.isHovered) {
	    		if (popup.destroy) {
	    		    popup.destroy();
	    		}
	    		else {
	    		    popup.destroy();
	    		}	
	    	}
	    }
	},

	/** Prevents the sentence popup from fading away.
	@param {WordSeer.view.visualize.wordtree.SentencePopup} popup The sentence
	popup.
	*/
	sentencePopupMouseEnter: function(popup) {
		popup.isHovered = true;
	},

	/** Sets a timeout for the the sentence popup to fade away 0.5s after the 
	user's mouse leaves it.
	@param {WordSeer.view.visualize.wordtree.SentencePopup} popup The sentence
	popup.
	*/
	sentencePopupMouseOut: function(popup) {
		popup.isHovered = false;
		var controller = this;
		controller.destroySentencePopupTimeOut = setTimeout(function(){
			controller.removePopup(popup);
		}, 500);
	},

	/** Called when the 'go to text' button in the
	{@link WordSeer.view.visualize.wordtree.SentencePopup} is clicked. Calls the
	DocumentsController's 
	{@link WordSeer.controller.DocumentsController#openDocument} method with the
	{@link WordSeer.view.visualize.wordtree.SentencePopup#documentId} and
	{@link WordSeer.view.visualize.wordtree.SentencePopup#sentenceId} of the
	sentence in the popup.
	*/
	sentencePopupGoToText: function(button) {
		var index = button.index;
		var popup = button.up('sentence-popup');
		var sentence = popup.getSentences()[index];
		this.getController('DocumentsController').openDocument(
			sentence.documentID, sentence.sentenceID);
	},
});