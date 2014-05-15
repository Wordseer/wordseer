/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** A BreadCrumb represents a single portion of the current query state.
A {@link WordSeer.view.widget.Widget Widget}'s final query is assembled by
combining all the the BreadCrumbs contained wihin the widget's
{@link WordSeer.view.search.BreadCrumbsPane BreadCrumbsPane}.
*/
Ext.define('WordSeer.view.search.BreadCrumb', {
   extend:'Ext.Container',
   alias:'widget.facet-breadcrumb',
   requires:[
    'WordSeer.view.wordmenu.WordMenu',
    'WordSeer.store.GrammaticalRelationsStore',
   ],
   layout:'column',
   bodyPadding:2,
   config:{
       record:{},
       type:"",
       class:"", // metadata OR word OR grammatical OR phrase-set OR phrase OR collection
       sentenceID: false,
       phrase: '',
       phraseId: -1,
       subsetModel: {},
   },
   autoEl:{
       cls:'breadcrumb',
   },
   initComponent:function(){
       this.addEvents('deleted', 'click', 'contextmenu');
       var me = this;
       var values = "";
       var record = this.getRecord();
       this.items = [];
       if(this.getClass() == "metadata"){
            var html = record.get('text');
            if (record.get('type') != "string") {
              html = record.get('range')[0] + " -- " + record.get('range')[1]
            }
           this.items = [
                {
                    xtype:'box',
                    autoEl:{
                        tag:'span',
                        cls:'property',
                        html:record.get('propertyName')+": ",
                    },
                },
                {
                    xtype:'box',
                    autoEl:{
                        tag:'span',
                        cls:'values',
                        html: html,
                    },
                },
            ];
        } else if(this.getClass() == "collection"){
            this.items = [
                {
                    xtype:'box',
                    autoEl:{
                        tag:'span',
                        cls:'collection',
                        html: "within: " + record.get('text')
                    }
                }
            ];
        } else if (this.getClass() == "phrase") {
          this.items = [
            {
              xtype: 'box',
              autoEl: {
                tag: 'span',
                cls: 'phrase',
                html: this.getPhrase(),
              }
            }
          ]
        } else {
          var govHTML = record.gov;
          if(record.govtype == 'phrase-set'){
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
            govHTML = ("<span class='relation'>all word forms of</span> "
              + govHTML);
          }

          var depHTML = record.dep;
          if(record.deptype == 'phrase-set'){
              depHTML = Ext.StoreManager.getByKey('PhraseSetStore')
               .getById(record.dep)
               .get('text');
          }

          if(this.getClass() == "word"){
            this.items = [
                 {
                     xtype:'box',
                     autoEl:{
                         tag:'span',
                         cls:'word',
                         html:govHTML
                     },
                     bodyPadding:2,
                 },
             ];
          } else if(this.getClass() == "grammatical"){
              this.items = [
                   {
                       xtype:'box',
                       autoEl:{
                           tag:'span',
                           cls:'gov',
                           html:govHTML
                       },
                   },
                   {
                       xtype:'box',
                       autoEl:{
                           tag:'span',
                           cls:'relation',
                           html: Ext.getStore('GrammaticalRelationsStore')
                            .getById(record.relation)
                            .get('name')
                       },
                   },
                   {
                       xtype:'box',
                       autoEl:{
                           tag:'span',
                           cls:'dep',
                           html:depHTML+" "
                       },
                   },
               ];
          };
        }
        this.items.push(
            {
                xtype:'checkbox',
                itemId:'checkbox',
                checked:true,
            }
        )
        this.items.push(
            {
                xtype:'image',
                cls:'close-button',
                src:("../../style/icons/x.png"),
                listeners:{
                    afterrender:function(){
                        this.getEl().on("click", function(){
                            me.fireEvent("deleted", me);
                      })
                    },
                }
            }
        )
        this.callParent();
   },
   /**
   @event click
   Fired when the breadcrumb is clicked.
   @param {WordSeer.view.search.BreadCrumb} breadcrumb The clicked breadcrumb.
   */
   listeners:{
        afterrender:function(){
            var width = 0;
            this.items.each(function(){
                width += this.getWidth()+6;
            })
            this.setWidth(width);
            var me = this;
            // Propagate clicks on the body of the breadcrumb, excluding the
            // control buttons.
            this.items.each(function(item) {
              if (item.xtype != 'checkbox' && item.xtype != 'image') {
                item.getEl().on('click', function(){
                  me.fireEvent('click', me);
                })
                item.getEl().on('contextmenu', function(){
                  me.fireEvent('contextmenu', me);
                })
              }
            })
        }
   },

   resetClass:function(){
   },
});
