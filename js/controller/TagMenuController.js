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
    */
    destroyMenu: function(view, record, element) {
        var candidates = Ext.ComponentQuery.query('wordseer-menu');
        var me = this;
        candidates.forEach(function(c) {
                c.close(10);
        });
    },
});
