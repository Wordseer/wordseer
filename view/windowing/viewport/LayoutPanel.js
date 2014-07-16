/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full 
 * license governing this code. */
/** Displays a single widget and tools for navigating search history, adding
other panel, and switching searches between widgets.
*/
Ext.define('WordSeer.view.windowing.viewport.LayoutPanel',  {
	extend:'Ext.container.Container',
    alias:'widget.layout-panel',
    config: {
        /**
        @cfg {WordSeer.model.LayoutPanelModel} layoutPanelModel The model
        instance that holds the history of searches for this layout panel.
        */
        layoutPanelModel: false
    },
    requires: [
        'WordSeer.view.menu.MenuOverlay',
    ],
    layout: 'fit',
    cls: 'inner',
    constructor: function(cfg) {
        this.initConfig(cfg);
        cfg.id = Ext.id(this, 'layoutpanel');
        this.formValues = {};
        var me = this;
        if (cfg.layoutPanelModel){
            this.formValues = cfg.layoutPanelModel.getFormValues();
        }
        var widget_options = APP.getSwitchableWidgets().map(function(w) {
            return {
                tag: 'option',
                cls: 'switch-widget',
                value: w.widget_xtype,
                html: w.text,
                selected: (w.widget_xtype == me.formValues.widget_xtype) ?
                    "selected" : ""
            };
        });
        // Create the DOMHelpers for the buttons.
        var button_actions = ['forward','back', 'close','save'];
        var nav_controls = button_actions.map(function(action) {
            return {
                tag: 'span',
                cls: 'nav-button nav-button-'+action,
                type: action,
           		enabled: 'true'
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
       var switcher = {
            tag: 'span',
            cls: 'switch-button ' + (is_last_panel? 'invisible' : '')
        };
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
                            type: 'frequent-words',
                            html: 'Co-occurring<br>Terms',

                        },
                        {
                            tag: 'span',
                            cls: 'panel-header-menubutton filters',
                            type: 'filters',
                            html: 'Filters'
                        },
                        {
                            tag: 'span',
                            cls: 'panel-header-menubutton sets',
                            type: 'sets',
                            html: 'Sets'
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
                    children:[],
                },
                {
                    tag: 'div',
                    cls: 'panel-render-target',
                    children: [],
                },
                switcher
            ]
        };
        var wrapped = [
            {
                xtype: 'container',
                itemId: 'inner',
                height: '100%',
                width: '100%',
                cls: 'inner',
                layout: {
                    type:'fit',
                    itemCls: 'fitted',
                },
                items: cfg.items,
                autoScroll: true,
            }
        ];
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
        this.addEvents(
            /**
            @event initSearch Fired on this panel when new set of FormValues
            needs to be displayed in a layoutPanel.
            @param {WordSeer.view.windowing.viewport.LayoutPanel} panel The
            panel in which to display the search.
            @param {WordSeer.model.FormValues} The FormValues object representing
            the new search.
            */
            'initSearch',
            /**
            @event newSlice Fired on this panel when the formValues needing
            to be displayed are a new slice.
            @param {WordSeer.view.windowing.viewport.LayoutPanel} panel The
            panel in which to display the search.
            @param {WordSeer.model.FormValues} The FormValues object representing
            the new search.
            */
            'newSlice',
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
            */
            'searchParamsChanged',
            /**
            @event navButtonClicked Fires whenever an action button is clicked.
            @param {WordSeer.view.windowing.viewport.LayoutPanel} The panel owning the action button.
            @param {String} type The type of button that was clicked. Currently
            either 'move', 'save','close','back', 'forward'.
            */
            'navButtonClicked',
            /**
            @event menuButtonClicked Fires whenever the user clicks on a menu button
            @param {WordSeer.view.windowing.viewport.LayoutPanel} The panel owning the button.
            @param {String} type The type of button
            @param {Ext.Element} clicked_el The element representing the clicked-on
            button.
            */
            'menuButtonClicked',
            /**
            @event switchWidgets Fires whenever the user changes the widget_xtype
            using the 'view as' drop-down menu on a menu button
            @param {WordSeer.view.windowing.viewport.LayoutPanel} The panel owning the button.
            @param {String} new_xtype The new view's widget_xtype
            */
            'switchWidgets',
            /**
            @event activate Notifies the rest of the app that this panel is the
            active one.
            @param {WordSeer.view.windowing.viewport.LayoutPanel} The panel
            */
            'activate'
            );
        var layout = this.getLayout();
        layout.getRenderTarget = function() {
            var target = this.owner.el.down('div.panel-render-target');
            this.innerCt = target;
            this.outerCt = target;
            return target;
        }
        this.callParent(arguments);
        this.addListener('afterrender', function(me) {
            me.populate();
        });
    },

    populate: function() {
        var me = this;
        me.getEl().on('click', function(event) {
            me.fireEvent('activate', me);
        })
        me.getEl().select('.nav-button').each(function(element) {
            element.on('click', function(event, clicked_el, clicked_dom) {
                me.fireEvent('navButtonClicked', me,
                    clicked_el.getAttribute('type'));
            });
        });

        me.getEl().select('.panel-header-menubutton').each(function(el) {
            el.on('click', function(event, clicked_el) {
                me.fireEvent('menuButtonClicked', me,
                    $(clicked_el).attr('type'), clicked_el);
            })
        })

        var select = me.getEl().down('.panel-header-widget-select');
        select.on('click', function(event) {
            me.fireEvent('activate', me);
        });
        select.on('change', function(event, clicked_el) {
            me.fireEvent('switchWidgets', me, $(this.dom).val());
        })
    }
})
