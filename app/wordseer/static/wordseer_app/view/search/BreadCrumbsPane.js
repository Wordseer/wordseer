/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Shows  {@link WordSeer.view.search.BreadCrumbs} corresponding to a given
search query represented by a {@link WordSeer.model.FormValues} object.
*/
Ext.define('WordSeer.view.search.BreadCrumbsPane', {
   extend:'Ext.Container',
   alias:'widget.breadcrumbs-pane',
   requires:[
    'WordSeer.view.search.BreadCrumb',
   ],
   itemId:'breadcrumbs',
   items:[],
   layout:'column',
   initComponent:function(){
        /**
        @event search Fired when the user issues a search query or when the tree
        is loaded for the first time.

        @param {WordSeer.model.FormValues} formValues a
        formValues object representing a search query.
        @param {WordSeer.view.search.BreadCrumbsPane} breadcrumbs This view.
        */
       this.addEvents('search'),
       this.callParent(arguments);
   },

   /** Displays a breadcrumb corresponding to a phrase or word acting as a
   filter.

   @param {WordSeer.model.PhraseModel | WordSeer.model.WordModel} model_instance
   The model instance representing the word or phrase acting as the filter.
   */
   addPhraseBreadCrumb:function(model_instance){
      var phrase = model_instance.get('sequence');
      var cls = "phrase";
      if (model_instance.get('class') == 'word') {
        phrase = model_instance.get('word');
      }
      var me = this;
      var id = 'phrase-'+model_instance.get('id');
      var oldCrumb = this.getComponent(id);
      if(oldCrumb){
          this.removeCrumb(oldCrumb);
      }
      var crumb = {
          class: cls,
          phrase: phrase,
          word: phrase,
          phraseId: model_instance.get('id'),
          itemId: id,
          record: model_instance,
      };
      this.addCrumb(crumb);
   },

   addCrumb:function(item){
       if(!this.getComponent(item.itemId)){
           var crumb = Ext.create(
               'WordSeer.view.search.BreadCrumb',
               item);
            crumb.pane = this;
            this.add(crumb);
       }
   },

   removeCrumb:function(crumb){
       if (crumb.getClass() == "collection") {
           if (this.record != null && this.record.removeUpdateListener != null && typeof(this.record.removeUpdateListener) == "function") {
               this.record.removeUpdateListener(this);
           }
           this.record = null;
       }
       var wasOn = crumb.getComponent('checkbox').getValue();
       if (this.getComponent(crumb.itemId)) {
          this.remove(crumb.itemId);
       }
   },

});
