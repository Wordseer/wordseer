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
            'tagmenu > wordseer-menuitem[action=removesort]': {
                click: this.removeSort,
            },
            'tagmenu > wordseer-menuitem[action=search]': {
                click: this.newSearch,
            },
            'tagmenu > wordseer-menuitem[action=resetsort]': {
                click: this.clearSort,
            },
        });
    },

    showTagMenu: function(tag_el, view){
        console.log(view.getStore().sorters);
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
        var menu = menuitem.up('tagmenu'),
            addnew = true,
            sorters = menu.view.getStore().sorters
            newsort = [];
        for (var i=0; i<sorters.items.length; i++){
            // check for direction change and duplication, and prevent a new
            // sorter from being added if either is found
            var sorter = {
                property: sorters.items[i].property,
                direction: sorters.items[i].direction,
            }
            if (sorter.property == menu.key){
                addnew = false;
                sorter.direction = menuitem.direction;
            }
            if (sorter.property != 'id') {
                newsort.push(sorter);
            }
        }
        if (addnew) {
            var newsorter = {
                direction: menuitem.direction,
                property: menu.key,
            }
            newsort.push(newsorter);
        }

        menu.view.getStore().sorters.clear();
        menu.view.getStore().sort(newsort);
        for (var i=0; i<newsort.length; i++){
            var tag = $('.metatag[metaname="' + newsort[i].property + '"]');
            tag.each(function(){
                $(this).addClass('sorting lev' + i)
                    .insertBefore($(this).siblings('.metatag').get(i));
                $(this).find('.key')
                    .append(' <span class="dir">[sort <i class="fa ' +
                    'fa-sort-amount-' + newsort[i].direction.toLowerCase() +
                    '"></i> '+(i+1)+']</span>');
            });
        }
    },

    clearSort: function(menuitem, e){
        var menu = menuitem.up('tagmenu');
        menu.view.getStore().sorters.clear();
        menu.view.getStore().sort("id");
    },

    removeSort: function(menuitem, e){
        var menu = menuitem.up('tagmenu'),
            sorters = menu.view.getStore().sorters
            newsort = [];
        for (var i=0; i<sorters.items.length; i++){
            // check for direction change and duplication, and prevent a new
            // sorter from being added if either is found
            var sorter = {
                property: sorters.items[i].property,
                direction: sorters.items[i].direction,
            }
            if (sorter.property != menu.key && sorter.property != 'id'){
                newsort.push(sorter);
            }
        }

        if (newsort.length == 0){
            newsort.push(
                {
                    property: 'id',
                    direction: 'ASC',
                }
            );
        }

        menu.view.getStore().sorters.clear();
        menu.view.getStore().sort(newsort);
        for (var i=0; i<newsort.length; i++){
            var tag = $('.metatag[metaname="' + newsort[i].property + '"]');
            tag.each(function(){
                $(this).addClass('sorting lev' + i)
                    .insertBefore($(this).siblings('.metatag').get(i));
                $(this).find('.key')
                    .append(' <span class="dir">[sort <i class="fa ' +
                    'fa-sort-amount-' + newsort[i].direction.toLowerCase() +
                    '"></i> '+(i+1)+']</span>');
            });
        }
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
