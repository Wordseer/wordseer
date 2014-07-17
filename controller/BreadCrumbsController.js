/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Manages interactions with {@link WordSeer.view.search.BreadCrumb}s and
{@link WordSeer.view.search.BreadCrumbsPane}s by alerting

*/
Ext.define('WordSeer.controller.BreadCrumbsController', {
	extend: 'Ext.app.Controller',
	views: [
		'search.BreadCrumb',
		'search.BreadCrumbsPane',
	],
	init: function() {
		this.control({
            'layout-panel': {
                newSlice: this.setBreadCrumbsForFormValues,
                breadCrumbDeleted: function(panel, breadcrumb) {
                    var widget = panel.down('widget');
                    var values = panel.getLayoutPanelModel().getFormValues()
                        .copy();
                    var cls = breadcrumb.breadcrumb_class;
                    var empty = Ext.create('WordSeer.model.FormValues', {});
                    if (cls == "metadata") {
                        var text = breadcrumb.record.get('text');
                        var value = breadcrumb.record.get('value');
                        for (var i = 0; i < values.metadata.length; i++) {
                            var record = values.metadata[i];
                            if (record.get('text') == text
                                && record.get('value') == value) {
                                values.metadata.splice(i, 1);
                            }
                        }
                    } else if (cls == "phrase") {
                        var text = breadcrumb.record.get('word');
                        for (var i = 0; i < values.phrases.length; i++) {
                            var record = values.phrases[i];
                            if (record.get('word') == text) {
                                values.phrases.splice(i, 1);
                            }
                        }
                    } else if (cls == "collection") {
                        values.collection = empty.collection;
                    } else if (cls == "word" || cls == "grammatical") {
                        values.gov = empty.gov;
                        values.dep = empty.dep;
                        values.relation = empty.relation;
                        values.deptype = empty.deptype;
                        values.govtype = empty.govtype;
                        for (var i = 0; i < values.search.length; i++) {
                            var record = breadcrumb.record;
                            var search = values.search[i];
                            var equal = true;
                            equal = equal && (search.gov == record.gov);
                            equal = equal && (search.dep == record.dep);
                            equal = equal && (search.relation == record.relation);
                            if (equal) {
                                values.search.splice(i, 1)
                            }
                        }
//                        console.log(values.search);
                        if (values.search.length > 0) {
                            var new_search = values.search[0];
                            values.gov = new_search.gov;
                            values.dep = new_search.dep;
                            values.relation = new_search.relation;
                            values.deptype = new_search.deptype;
                            values.govtype = new_search.govtype;
                        }
                    }
                    widget.setFormValues(values);
                    panel.fireEvent('searchParamsChanged', panel, values);
                }
            },
			'facet-breadcrumb > checkbox': {
				change:function(checkbox) {
                checkbox.up('widget').fireEvent('searchParamsChanged',
                	checkbox.up('widget'));
            	}
            }
		})
	},

    /** Adds {@link WordSeer.view.search.BreadCrumb}s corresponding to the
    given {@link WordSeer.model.FormValues formValues} to the
    given {@link WordSeer.view.search.BreadCrumbsPane}. Called by
    {@link WordSeer.controller.WindowingController#playHistoryItem}.

    @param {WordSeer.model.FormValues} formValues The
    {@link WordSeer.search.SearchController formValues} formValues object
    containing the search parameters.

    @param {WordSeer.view.search.BreadCrumbsPane} breadcrumbs The BreadCrumbsPane
    to which to add the {@link WordSeer.view.search.BreadCrumb}s.
    */
    setBreadCrumbsForFormValues: function(panel, formValues) {
        panel.getEl().down('div.breadcrumbs').update('');
        panel.getLayoutPanelModel().breadcrumbs = [];
        var breadcrumbs = [];
        // Add the search breadcrumbs.
        if (formValues.search) {
            for (var i = 0; i < formValues.search.length; i++) {
                breadcrumbs.push(
                    this.addSearchBreadCrumb(formValues.search[i], i,
                        formValues.widget_xtype));
            }
        }
        // Add the phrase breadcrumbs.
        if (formValues.phrases) {
            var phrases = formValues.phrases;
            for (var i = 0; i < phrases.length; i++) {
                breadcrumbs.push(
                    this.addPhraseBreadCrumb(phrases[i]));
            }
        }
       if (formValues.metadata) {
            var metadata = formValues.metadata;
            for (var i = 0; i < metadata.length; i++) {
                var record = metadata[i];
                breadcrumbs.push(
                    this.addMetadataBreadCrumb(record));
            }
        }
        // Add the collection breadcrumb
        if (formValues.collection) {
            if (formValues.collection !=  'all') {
                breadcrumbs.push(
                    this.addCollectionBreadCrumb(formValues.collection));
            }
        }
        var breadcrumbs_pane = panel.getEl().down('div.breadcrumbs');
        breadcrumbs.forEach(function(domHelper, index) {
            domHelper.index = index;
            domHelper.panel_id = panel.id;
            breadcrumbs_pane.appendChild(domHelper);
        });
        panel.getLayoutPanelModel().breadcrumbs = breadcrumbs;
        breadcrumbs_pane.select('span.breadcrumb').each(function(el) {
            var index = parseInt(el.getAttribute('index'));
            var panel_id = el.getAttribute('panel_id');
            var panel = Ext.getCmp(panel_id);
            var crumb_data = panel.getLayoutPanelModel().breadcrumbs[index];
            el.down('span.breadcrumb-close').on('click', function() {
                panel.fireEvent('breadCrumbDeleted', panel, crumb_data);
            });
        });
    },

    addSearchBreadCrumb:function(formValues, index, widget_xtype) {
        var style = {};
        var values = Ext.apply({
            gov:'',
            dep:'',
            relation:2,
        }, formValues);
        var type = "grammatical";
        if (values.relation == 2) {
            type = "word";
        }
        var id = (values.gov + " " + values.dep + " " + values.relation + " " +
            values.all_word_forms);
        if (widget_xtype == "column-vis-widget" ||
            widget_xtype == "word-frequencies-widget") {
            //color the item appropriately
            var color = COLOR_SCALE(index);
            var rgb = d3.rgb(color);
            style = ("color:" + color + ";" +
                "background-color:" +
                "rgba(" + rgb.r + "," + rgb.g + "," + rgb.b + ",0.2);");
        }
        var crumb = values;
        crumb.breadcrumb_class = type;
        crumb.style = style;
        crumb.record = values;
        return  this.makeCrumb(crumb);
    },

    addMetadataBreadCrumb: function(record) {
       var type = record.get('type');
       var propertyName = record.get('propertyName');
       var value = record.get('value');
       var range = record.get('range');
        var id = 'metadata'+type+propertyName;
        if(type == "string"){
            id += value;
        }
        var crumb = {
            breadcrumb_class: 'metadata',
            record: record,
        };
        return this.makeCrumb(crumb);
    },

    addCollectionBreadCrumb:function(record) {
       var collection = record.get('text');
       var id = 'collection-'+collection;
       var crumb = {
           breadcrumb_class: 'collection',
           values:collection,
           subsetModel: record,
           record: record,
       };
       return this.makeCrumb(crumb);
    },

    addPhraseBreadCrumb:function(model_instance){
       var phrase = model_instance.get('sequence');
       var cls = "phrase";
       if (model_instance.get('class') == 'word') {
         phrase = model_instance.get('word');
       }
       var crumb = {
           breadcrumb_class: cls,
           phrase: phrase,
           word: phrase,
           phraseId: model_instance.get('id'),
           record: model_instance,
       };
       return this.makeCrumb(crumb);
    },

    makeCrumb: function(cfg) {
        var el = {
            tag: 'span',
            cls: 'breadcrumb',
        };
        Ext.apply(el, cfg);
        var breadcrumb_class = cfg.breadcrumb_class;
        var values = "";
        var record = cfg.record;
        var crumb = {
            tag: 'span',
            cls: 'breadcrumb-contents',
        };
        crumb.children = [];
        if (breadcrumb_class == "metadata") {
             var html = record.get('text');
             if (record.get('type') != "string") {
               html = record.get('range')[0] + " -- " + record.get('range')[1];
             }
            crumb.children = [
                 {
                      tag:'span',
                      cls:'values',
                      html: html,
                  },
                  {
                      tag:'span',
                      cls:'property',
                      html:record.get('propertyName')
                  },
             ];
         } else if (breadcrumb_class == "collection") {
             crumb.children = [
                {
                  tag:'span',
                  cls:'collection',
                  html: "within: " + record.get('text')
                }
             ];
         } else if (breadcrumb_class == "phrase") {
               crumb.children = [
                 {
                     tag: 'span',
                     cls: 'phrase',
                     children: [
                        {
                            tag: 'span',
                            cls:'word',
                            html: cfg.phrase,
                        },
                        {
                            tag: 'span',
                            cls: 'relation',
                            html: 'any match'
                        }
                     ]
                   }
               ];
         } else {
               var govHTML = record.gov;
               if (record.govtype == 'phrase-set') {
                    var govItem = Ext.StoreManager.getByKey('PhraseSetStore').getById(
                      record.gov);
                    if (govItem) {
                       govHTML = govItem.get('text');
                    }
                    else {
                       govHTML = "{  }";
                    }
               }
               if (record.all_word_forms) {
                 govHTML = ("<span class='relation'>all word forms of</span> " +
                    govHTML);
               }
               var depHTML = record.dep;
               if (record.deptype == 'phrase-set') {
                   depHTML = Ext.StoreManager.getByKey('PhraseSetStore')
                    .getById(record.dep)
                    .get('text');
               }
               if (breadcrumb_class == "word") {
                    crumb.children = [
                        {
                              tag:'span',
                              cls:'word',
                              html:govHTML
                        }
                    ];
               } else if (breadcrumb_class == "grammatical") {
                    crumb.children = [
                         {
                            tag:'span',
                            cls:'gov',
                            html:govHTML
                        },
                        {
                            tag:'span',
                            cls:'relation',
                            html: Ext.getStore('GrammaticalRelationsStore')
                            .getById(record.relation)
                            .get('name')
                        },
                        {
                            tag:'span',
                            cls:'dep',
                            html:depHTML + " "
                        },
                    ];
                }
        }
        var controls = {
            tag:'span',
            cls:'breadcrumb-controls',
            children: [
                {
                   tag: 'span',
                   cls: 'breadcrumb-close breadcrumb-control',
                }
            ]
        };
        el.children = [crumb, controls];
        return el;
    },
});
