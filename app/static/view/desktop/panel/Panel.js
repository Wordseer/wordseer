/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/**
Displays a single widget and tools for navigating search history, adding
other panel, and switching searches between widgets.
*/
Ext.define('WordSeer.view.desktop.panel.Panel',{
    extend:'Ext.container.Container',
    alias:'widget.simple-panel',
    config: {
        /**
        @cfg {WordSeer.model.LayoutPanelModel} layoutPanelModel The model
        instance that holds the history of searches for this layout panel.
        */
        layoutPanelModel: false
    },
    layout: 'fit',

    constructor: function(cfg) {
        cfg.id = Ext.id(this, 'layoutpanel');
        var widget_options = APP.getWidgets().map(function(w) {
            return {
                tag: 'option',
                value: w.widget_xtype,
                html: w.text,
            }
        });
        // Create the tags for the buttons.
        var button_actions = ['move', 'save', 'close', 'back', 'forward'];
        var nav_controls = button_actions.map(function(action) {
            return {
                tag: 'span',
                cls: 'nav-button nav-button-'+action,
                type: action
            }
        });
        // Check if this is the last panel in the line. If not, show the panel
        // switcher.
        var is_last_panel = true;  // By default, assume there's only one panel.
        if (cfg.layoutPanelModel) {
            var layout = Ext.getStore('LayoutStore').getById(
                cfg.layoutPanelModel.get('layout_id'));
            if (layout) {
                last = layout.panels().getAt(layout.panels().count -1)
                if (last) {
                    is_last_panel = (last == cfg.layoutPanelModel);
                }
            }
        }
        nav_controls.push({
            tag: 'span',
            cls: 'switch-button ' + is_last_panel? 'invisible' : ''
        });

        cfg.autoEl = {
            tag: 'div',
            cls: 'panel',
            children: [
                {
                    tag: 'div',
                    cls: 'panelheader',
                    children: [
                        {
                            tag: 'div',
                            cls: 'panel-header-navcontrols',
                            children: nav_controls,
                        },
                        {
                            tag: 'span',
                            cls: 'panel-header-menubutton frequent-words',
                            html: 'Frequent Words',

                        },
                        {
                            tag: 'span',
                            cls: 'panel-header-menubutton filters',
                            html: 'Filters'
                        },
                        {
                            tag: 'select',
                            cls: 'panel-header-widget-select',
                            children: widget_options
                        },
                    ]
                },
                {
                    tag:'div',
                    cls:'breadcrumbs',
                    html: 'Breadcrumbs here'
                },
                {
                    tag: 'div',
                    cls: 'panel-render-target',
                    children: [],
                }
            ]
        }
        var wrapped = [
            {
                xtype: 'container',
                items: cfg.items,
                layout: cfg.layout
            }
        ]
        cfg.items = wrapped;
        cfg.layout = 'fit';
        this.initConfig(cfg);
        this.callParent(arguments);
    },

    /**
    @property {WordSeer.model.FormValues} formValues The current formValues
    being displayed by this panel.

    */
    formValues: null,

    initComponent: function() {
        /**
        @event searchParamsChanged
        Fired by components within this panel whenever the user performs a
        search or browsing action that necessitates a change in the data
        displayed by this widget. The
        {@link WordSeer.controller.SearchController#searchParamsChanged} method
        listens for this event and responds to it by calculating the new search
        parameters and {@link WordSeer.model.HistoryItemModel history item}
        (based on the user's interactions with the widget) and telling the
        widget to issue a new search with the updated history item.

        @event navButtonClicked Fires whenever an action button is clicked.
        @param {WordSeer.view.desktop.panel.Panel} The panel owning the action button.
        @param {String} type The type of button that was clicked. Currently
        either 'move', 'save','close','back', 'forward'.

        */
        this.addEvents('searchParamsChanged', 'navButtonClicked');
        var layout = this.getLayout();
        layout.getRenderTarget = function() {
            var target = this.owner.el.down('div.panel-render-target');
            this.innerCt = target;
            this.outerCt = target;
            return target;
        }
        this.callParent(arguments);
    },

    listeners: {
        afterrender: function(me) {
            me.populate();
        },
        navButtonClicked: function(me, type) {
            console.log('Nav button of type ' + type + ' clicked');
        }
    },

    populate: function() {
        var me = this;
        console.log('populating a layout panel');
        me.getEl().select('.nav-button').each(function(element) {
            element.on('click', function(event, clicked_el, clicked_dom) {
                me.fireEvent('navButtonClicked', me,
                    clicked_el.getAttribute('type'));
            });
        });
    }
})
