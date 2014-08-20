/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Controls:

- Clicks and actions on the {@link WordSeer.view.wordmenu.WordMenu word menu}:
		- {@link WordSeer.view.wordmenu.WordMenu#hide Word Menu hide}
		- {@link WordSeer.view.wordmenu.LauncherButton#click Launcher Button click}
		- {@link WordSeer.view.wordmenu.GrammaticalSearchOption#click GrammaticalSearchOption click}
- Clicks on words in the following views:
		- {@link WordSeer.view.search.BreadCrumb#click BreadCrumb}
		- {@link WordSeer.view.document.DocumentViewer#wordclicked DocumentViewer}
		- {@link WordSeer.view.sentence.SentenceList#wordclicked SentenceList}
		- {@link WordSeer.view.Word#click Word}
**/
Ext.define('WordSeer.controller.WordMenuController',{
	extend: 'Ext.app.Controller',
	views: [
		'document.DocumentViewer',
		'search.BreadCrumb',
		'sentence.SentenceList',
		'Word',
		'wordmenu.WordMenu',
		'menu.Menu',
		'menu.MenuItem',
		'relatedwords.RelatedWordsPopup'
	],
	stores: [],
	models: [
		'WordModel',
	],
	init: function() {
//		console.log('WordMenu controller initialized.');
		this.control({
			'document-viewer, sentence-list, sentence-table': {
				wordclicked: this.fromHTMLSpan
			},
			'word': {
				click: this.fromWordClick,
			},
			'facet-breadcrumb': {
				click: this.fromBreadcrumb,
				contextmenu: this.fromBreadcrumb
			},
			'wordmenu': {
				hide: this.hideWordMenu
			},
			'word-tree': {
				'nodecontextmenu': this.fromWordTreeNode
			},
			'launcherbutton': {
				click: this.launcherButtonClicked,
			},
			'grammaticalsearchoption': {
				click: this.grammaticalSearchOptionClicked,
			},
			'related-words-list': {
				itemClick: this.fromRelatedWordClick,
				//itemMouseLeave: this.destroyMenu,
			},
			'synset-list': {
				tagClicked: this.fromSynsetListClick,
			},
			'set-list': {
				itemMouseEnter: this.fromSet,
				itemMouseLeave: this.destroyMenu
			},
			'wordmenu > wordseer-menuitem[action=nearbywords]': {
				click: this.showNearbyWords,
			},
			'wordmenu > wordseer-menuitem[action=similarwords]': {
				click: this.showSimilarWords,
			},
			'frequent-words': {
				itemClick: this.fromFrequentWord,
				//itemMouseLeave: this.destroyMenu
			},
			'wordmenu > wordseer-menuitem[action=get-nearby-word-matches]': {
				click: this.getNearbyWordMatches,
			},
			'wordmenu > wordseer-menuitem[action=filter]': {
				click: this.filterByClickedWord
			},
			'wordseer-menuitem[action=search-for-phrase]': {
				click: this.searchForPhrase
			}


		});
	},

	/** The user has clicked on a word in the
	{@link WordSeer.view.frequentwords.FrequentWordsList}. Instantiate
	a new {@link WordSeer.view.wordmenu.WordMenu word menu} with a
	{@link WordSeer.model.WordModel model} corresponding to the clicked-on word.

	@param {WordSeer.view.frequentwords.FrequentWordsList} view The list of
	related words
	@param {WordSeer.model.WordModel} word_model_instance The clicked-on word.
	*/
	fromFrequentWord: function(view, word_model_instance, row_element){
		view.getEl().select('tr.hovered').removeCls('hovered');
		$(row_element).addClass('hovered');
		var menu = this.showWordMenu(word_model_instance, row_element, view);
		view.up('overlay').menuActive = menu;
		return false;
	},

	/** The user has clicked on a {@link WordSeer.view.Word word}. Instantiates
	a new {@link WordSeer.view.wordmenu.WordMenu word menu} with the
	{@link WordSeer.view.Word word}'s {@link WordSeer.model.WordModel model}
	and shows it next to the word.
	*/
	fromWordClick: function(word_view, event){
		this.showWordMenu(word_view.getRecord(), word_view, word_view);
		$(word_view.getEl().dom).addClass('menu-word');
	},

	/** The user has clicked on a word in the
	{@link WordSeer.view.relatedwords.RelatedWordsList}. Instantiates
	a new {@link WordSeer.view.wordmenu.WordMenu word menu} with the
	a new  {@link WordSeer.model.WordModel model}
	instance representing the word, and shows it next to the word.

	@param {WordSeer.view.relatedwords.RelatedWordsList} view
	The list of related words

	@param {Ext.data.Model} record The record corresponding to the
	clicked-on word

	@param {HTMLElement} clicked_view The HTML element of the clicked view.
	*/
	fromRelatedWordClick: function(view, record, clicked_el){
		var word = Ext.create('WordSeer.model.WordModel',
			{
				word:record.get('word'),
				id: record.get('id'),
				class:'word',
			});
		var popup = view.up('related-words-popup');
		word.formValues = popup.formValues;
		word.related = popup.current;
		var menu = this.showWordMenu(word, clicked_el, view);
		view.up('overlay').menuActive = menu;
	},

	fromSynsetListClick: function(view, record, clicked_el) {
		var word = Ext.create('WordSeer.model.WordModel',
			{
				word:record.get('word'),
				id: record.get('id'),
				class:'word',
			});
		var popup = view.up('synsets-popup');
		word.related = popup.current;
		var menu = this.showWordMenu(word, clicked_el, view);
		view.up('overlay').menuActive = menu;
	},

	/** The user has clicked on a HTMLElement word while viewing a document or
	a list of search results. Creates a new {@link WordSeer.model.WordModel}
	instance with the information in the span, instantiates a
	{@link WordSeer.view.wordmenu.WordMenu word menu} based on that WordModel,
	and shows it next to the HTML Element.

	@param {HtmlSpanElement} The clicked-on word. The HTML span has the
	following attributes:
		word-id: The ID of the word
		sentence-id: the id of the sentence in which the word appears
	The text of the HTML span is the word.
	*/
	fromHTMLSpan: function(word_element) {
		var word = Ext.create('WordSeer.model.WordModel',
			{
				id: $(word_element).attr('word-id'),
				word: $(word_element).text(),
				position: $(word_element).attr('position'),
				class:'word',
				sentenceID: $(word_element).attr('sentence-id'),
			});
		var container_id = word_element.getAttribute('container-id');
		var view = Ext.getCmp(container_id);
		this.showWordMenu(word, word_element, view);
		$(word_element).addClass('menu-word');
		return false;
	},

	/** The user has clicked on a
	{@link WordSeer.view.search.BreadCrumb breadcrumb}. Creates a new
	{@link WordSeer.model.WordModel} instance with the information in the
	breadcrumb, instantiates a {@link WordSeer.view.wordmenu.WordMenu word menu}
	based on that WordModel, and shows it next to the BreadCrumb.

	@param {WordSeer.view.search.BreadCrumb} breadcrumb The clicked-on
	breadcrumb.
	*/
	fromBreadcrumb: function (breadcrumb) {
		var current = null;
		if (breadcrumb.getClass() == "word" || (breadcrumb.getClass() ==
			"grammatical" || breadCrumb.getClass() == "grammatical")) {
			current = Ext.create('WordSeer.model.WordModel', {
				class: breadcrumb.getClass(),
				word: breadcrumb.getGov(),
				sentenceID: breadcrumb.getSentenceID(),
				gov: breadcrumb.getGov(),
				dep: breadcrumb.getDep(),
				relation: breadcrumb.getRelation(),
				govtype: breadcrumb.getGovtype(),
				deptype: breadcrumb.getDeptype(),
			});
		}
		this.showWordMenu(current, breadcrumb);
		breadcrumb.addClass('menu-word');
	},

	/** Causes a {@link WordSeer.view.wordmenu.WordMenu} to show up next to
	a word tree node when it's clicked on. This only shows a menu next to
	single words, and not phrases, because the word menu doesn't handle phrases
	except to search for them.

	@param {SVGElement} node The svg element representing the node that was
	hovered over.
	@param {Object} d The object containing the data for the node that was
	clicked.
	*/
	fromWordTreeNode: function(node, d) {
		var text = d.key;
		var cls = text.indexOf(' ') != -1 ? 'phrase' : 'word';
		var current = Ext.create('WordSeer.model.WordModel', {
			class: cls,
			id: "??",
			word: text,
		});
		this.showWordMenu(current, node);
		return false;
	},

	/** Instantiates a new word menu and shows it next to passed-in element by
	calling the {@link Ext.menu.Menu#showBy} method on the menu.

	@param {WordSeer.model.WordModel} current The WordModel representing the
	clicked-on word.

	@param {Ext.Element|HTMLElement} shownBy The component on the page next to
	which the new menu should be shown.
	*/
	showWordMenu: function (current, shownBy, view) {
		this.destroyMenu();
		var formValues = {};
		var current_layout_model = Ext.getStore('LayoutStore').getCurrent();
		var viewport = Ext.getCmp('windowing-viewport').getComponent(
			current_layout_model.get('id'));
		if (viewport) {
			var current_panel = viewport.getCurrentPanel();
			var widget = current_panel.down('widget');
			if (widget) {
				formValues = widget.getFormValues();
			}
		}
		var menu = Ext.create('WordSeer.view.wordmenu.WordMenu', {
			current: current,
			shownBy:shownBy,
			view: view,
			formValues: formValues
		});
		if(shownBy instanceof Array) {
			menu.showAt(shownBy);
		} else {
			menu.showBy(shownBy, 'tl-bl?');
		}
		return menu;
	},

	/**
	Destroys the current word menu.
	*/
	destroyMenu: function(view, record, element) {
		var candidates = Ext.ComponentQuery.query('wordseer-menu');
		var me = this;
		candidates.forEach(function(c) {
				c.close(10);
		});
	},

	/** Resets the class of the clicked-on word after the
	{@link WordSeer.view.wordmenu.WordMenu word menu} fires its `hide` event.
	*/
	hideWordMenu:function(menu) {
		if (menu.getShownBy().resetClass === undefined) {
			$(menu.getShownBy()).removeClass('menu-word');
		} else {
			menu.getShownBy().resetClass();
		}
	},

	/** The user has clicked on a
	{@link WordSeer.view.wordmenu.GrammaticalSearchOption}. Asks the
	{@link WordSeer.controller.SearchController SearchController} to issue a new
	search using the parameters of the clicked-on menu item.

	@param {WordSeer.view.wordmenu.GrammaticalSearchOption} button The
	clicked-on {@link WordSeer.view.wordmenu.WordMenu word menu} item.
	*/
	grammaticalSearchOptionClicked: function(button) {
		var current = button.getCurrent();
		var relation = button.getRelation();
		var search_term = (button.getCurrent().getClass() == 'word' ?
			button.getCurrent().get('word') : button.getCurrent().get('id'));
		var search_type = button.getCurrent().getClass();
		var gov = button.getGov() ? button.getGov() : '';
		var gov_type = button.getGov()? search_type : 'word';
		var dep = button.getDep() ? button.getDep() : '';
		var dep_type = button.getDep()? search_type : 'word';
		var word_model_instance = Ext.create('WordSeer.model.WordModel', {
			word: button.getCurrent().get('word'),
			class: 'grammatical',
			gov: gov,
			govtype: gov_type,
			dep: dep,
			deptype: dep_type,
			relation: relation,
		});
		var widget_xtype = 'search-widget';
		if (relation === "") {
			widget_xtype = 'sentence-list-widget';
		}
		this.getController('SearchController').searchWith(
			{widget_xtype: widget_xtype}, word_model_instance
		);
	},

	/** The user has clicked on a
	{@link WordSeer.view.wordmenu.LauncherButton}. Asks the
	{@link WordSeer.controller.SearchController SearchController} to issue a new
	search using the parameters of the clicked-on menu item.

	@param {WordSeer.view.wordmenu.LauncherButton} button The clicked-on button.
	*/
	launcherButtonClicked: function(button) {
		this.getController('SearchController').searchWith(
			button.getWidget(), button.getCurrent());
	},

	/** Shows a popup displaying the nouns, verbs and adjectives that occur
	most frequently in sentences containing the clicked-on word.
	@param {Ext.menu.Item} menuitem The word menu item that was clicked.
	*/
	showNearbyWords: function(menuitem) {
		var data = menuitem.data;
		var position = menuitem.getPosition();
		var popup = Ext.create('WordSeer.view.relatedwords.RelatedWordsPopup', {
			data: data,
			current: menuitem.up('wordmenu').getCurrent(),
			formValues: menuitem.up('wordmenu').getFormValues()
		});
		popup.showAt(position[0], position[1]);
	},

	/** Shows a popup displaying the words that occur in similar contexts
	to the clicked-on word.
	@param {Ext.menu.Item} menuitem The word menu item that was clicked.
	*/
	showSimilarWords: function(menuitem) {
		var synsets = menuitem.data;
		var position = menuitem.getPosition();
		if (synsets.length > 0) {
			var synsets_popup = Ext.create('WordSeer.view.relatedwords.SynsetPopup', {
				data: synsets,
				current: menuitem.up('wordmenu').getCurrent()
			});
			synsets_popup.showAt(position[0], position[1]);
		}
	},
	/** Does a search for the two related words in the same sentence.
	*/
	getNearbyWordMatches: function(menuitem) {
		var menu = menuitem.up('wordmenu');
		var current = menu.getCurrent();
		var related = current.related;
		var formValues = current.formValues;
		var gov = "+"+current.get('word') + " +" + related.get('word');
		var new_form_values = formValues.copy();
		new_form_values.gov = gov;
		new_form_values.govtype = "word";
		new_form_values.widget_xtype = "sentence-list-widget";
		new_form_values.search = [];
		new_form_values.search.push({
				gov: new_form_values.gov,
				dep: new_form_values.dep,
				relation: new_form_values.relation,
				govtype: new_form_values.govtype,
				deptype: new_form_values.deptype,
			});
		var history_item = this.getController('HistoryController')
			.newHistoryItem(new_form_values);
		this.getController('WindowingController')
			.playHistoryItemInNewPanel(history_item.get('id'));
	},

	/** Adds a new filter by the clicked word or phrase to the parent
	{@link WordSeer.view.widget.Widget}'s {@link WordSeer.model.FormValues}.

	@param {WordSeer.view.menu.MenuItem} menuitem  The menu item that was
	clicked.
	*/
	filterByClickedWord: function(menuitem) {
		var menu = menuitem.up('wordmenu');
		var view = menu.getView();
		var panel = view.up('layout-panel');
		var current_word = menu.getCurrent().get('word');
		if (panel) {
			var formValues = panel.getLayoutPanelModel().getFormValues().copy();
			var filtered = formValues.phrases.filter(function(item) {
				return item.get('word') == current_word;
			});
			if (filtered.length === 0) {
				formValues.phrases.push(menu.getCurrent());
				panel.fireEvent('searchParamsChanged', panel, formValues);
			}
		}
	},

	searchForPhrase: function(menuitem) {
		var parentMenuItem = menuitem.up().parentMenuItem;
		var phrase = parentMenuItem.text;
		var word_model_instance = Ext.create('WordSeer.model.WordModel', {
			word: phrase,
			class: 'grammatical',
			gov: phrase,
			govtype: 'word',
			dep: '',
			deptype: 'word',
			relation: '',
		});
		this.getController('SearchController').searchWith(
			{widget_xtype: 'sentence-list-widget'}, word_model_instance
		);
	}
});
