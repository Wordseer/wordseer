/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Displays a single widget and tools for navigating search history, adding
other panel, and switching searches between widgets.
*/
Ext.define('WordSeer.view.windowing.viewport.LandingPage',  {
	extend:'Ext.container.Container',
    alias:'widget.landing-page',
    config: {
        /**
        @cfg {WordSeer.model.LayoutPanelModel} layoutPanelModel The model
        instance that holds the history of searches for this layout panel.
        */
        layoutPanelModel: false,
    },
    requires: [
      'WordSeer.view.overview.FrequentWordsOverview',
      'WordSeer.view.overview.MetadataOverview',
      'WordSeer.view.overview.SetsOverview',

    ],
    layout: {
        type: 'hbox',
        align: 'stretch'
    },
    cls: 'inner',
    constructor: function(cfg) {
        this.initConfig(cfg);
        this.layoutPanelModel = Ext.create('WordSeer.model.LayoutPanelModel');
        cfg.id = Ext.id(this, 'landing-page');
        this.formValues = {};
        var me = this;
        if (cfg.layoutPanelModel){
            this.formValues = cfg.layoutPanelModel.getFormValues();
        }
        this.layoutPanelModel.getPhrasesStore().load({params:{length:2,
            has_function_words:0}});
        this.layoutPanelModel.getTopN().load({params:{pos:'N'}});
        this.layoutPanelModel.getTopV().load({params:{pos:'V'}});
        this.layoutPanelModel.getTopJ().load({params:{pos:'J'}});

        cfg.autoEl = {
            tag: 'div',
            cls: 'landing-page',
            children: [
                {
                    tag: 'div',
                    cls: 'main-header',
                    children: [
                        {
                            tag: 'a',
                            href: '/projects',
                            cls: 'all-projects',
                            html: "&laquo; All projects"
                        },
                        {
                            tag: 'h1',
                            cls: 'main-header',
                            html: $('title').text(),
                        },
                        {
                            tag: 'div',
                            cls: 'neh-logo'
                        }
                    ]
                },
                {
                    tag: 'div',
                    cls: 'landingpage-render-target',
                    children: []
                }
            ]
        };
        // var wrapped = [
        //     {
        //         xtype: 'container',
        //         itemId: 'inner',
        //         cls: 'inner',
        //         layout: 'fit',
        //         items: cfg.items,
        //         autoScroll: true,
        //     }
        // ];
        // cfg.items = wrapped;
        // cfg.layout = 'fit';
        this.initConfig(cfg);
        this.callParent(arguments);
    },

    initComponent: function() {
        var layout = this.getLayout();
        layout.getRenderTarget = function() {
            var target = this.owner.el.down('div.landingpage-render-target');
            this.innerCt = target;
            this.outerCt = target;
            return target;
        };
        this.items = [
            {
                xtype: 'frequent-words-overview',
                model: this.getLayoutPanelModel(),
            },
            {
                xtype: 'metadata-overview',
                model: this.getLayoutPanelModel(),
            },
            {
                xtype: 'sets-overview',
                model: this.getLayoutPanelModel()
            }
        ];
        this.callParent(arguments);
        this.addListener('afterrender', function(me) {
            me.populate();
        });
    },

    populate: function() {
        var me = this;
    }
});
