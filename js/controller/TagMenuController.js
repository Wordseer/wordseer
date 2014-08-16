/** Controls:

- Clicks and actions on the {@link WordSeer.view.tagmenu.TagMenu tag menu}:
        - tk
- Clicks on metadata tags in the {@link WordSeer.view.sentence.SentenceList#tagclicked SentenceList}

**/

Ext.define('WordSeer.controller.TagMenuController', {
    extend: 'Ext.app.Controller',
    views: [
        // 'tagmenu.TagMenu',
        'sentence.SentenceList',
        'menu.Menu',
    ],
    stores: [],
    models: [
        'MetadataModel',
    ],

    init: function(){
        this.control({
            'sentence-list': {
                tagclicked: this.showTagMenu,
            },
            'tagmenu > wordseer-menuitem[action=filter]': {
                click: this.applyFilter,
            },
            'tagmenu > wordseer-menuitem[action=sort]': {
                click: this.sortSentences,
            },
            'tagmenu > wordseer-menuitem[action=search]': {
                click: this.newSearch,
            },
            'tagmenu > wordseer-menuitem[action=clearsort]': {
                click: this.clearSort,
            },
        });
    },

    showTagMenu: function(tag_el, view){
        this.destroyMenu();
        $(tag_el).addClass("active");
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
        };

        var menu = Ext.create('WordSeer.view.menu.TagMenu', {
            shownBy: tag_el,
            view: view,
        });
        menu.showBy(menu.shownBy);
        return menu;
    },

    /**
    Destroys the current word menu.
    **/
    destroyMenu: function(view, record, element) {
        var candidates = Ext.ComponentQuery.query('wordseer-menu');
        var me = this;
        candidates.forEach(function(c) {
                c.close(10);
        });
    },

    /**
    Applies the selected filter to the current panel and triggers a new search
    **/
    applyFilter: function(menuitem, e){
        var menu = menuitem.up('tagmenu');
        var panel = menu.view.up('layout-panel');
        var filter_record = Ext.create('WordSeer.model.MetadataModel', {
            text: menu.value,
            value: menu.value,
            propertyName: menu.key,
        });
        panel.formValues.metadata.push(filter_record);
        panel.down('widget').setFormValues(panel.formValues);
        this.getController('SearchController').searchParamsChanged(panel,
            panel.formValues);
    },

    sortSentences: function(menuitem, e){
        var menu = menuitem.up('tagmenu');
        menu.view.getStore().sort(menu.key, menuitem.direction);
        $('.metatag[metaname="' + menu.key + '"]').addClass('sorting');
        $('.sorting .key').append(' <span class="dir">[sort <i class="fa ' +
            'fa-sort-amount-' + menuitem.direction.toLowerCase() +
            '"></i> ]</span>');
    },

    clearSort: function(menuitem, e){
        var menu = menuitem.up('tagmenu');
        menu.view.getStore().sort('id');
    },

    newSearch: function(menuitem, e) {
        var menu = menuitem.up('tagmenu');
        var meta_record = Ext.create('WordSeer.model.MetadataModel', {
            text: menu.value,
            value: menu.value,
            propertyName: menu.key,
        });
        var newsearch = {
            class: 'metadata',
            metadata: [meta_record],
        };

        this.getController('SearchController').searchWith(
            {widget_xtype: 'sentence-list-widget'}, newsearch);
    }
});
