/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.document.ContentsPane',{
    extend:'Ext.panel.Panel',
    alias:'widget.contents-pane',
     height:500,
     width:100,
     title:'Contents',
     autoScroll:true,
     draw: function() {
         var container = this.up().getComponent('viewer').getEl().dom;
         var html = this.makeSubUnitsHTML($(container).find("div.document"));
         this.getEl().update(html);
     },
     resetCurrent: function(){
         var container = $(this.getEl().dom);
         container.find('ul').removeClass("current");
     },
     setCurrent: function(unitName, unitId, unitTitle) {
         var container = $(this.getEl().dom);
         container.find('ul[unit-id="'+unitId+'"][unit-name="'+unitName+'"]')
                    .addClass("current");
     },
     makeSubUnitsHTML: function(dom) {
         var unitId = dom.attr("unit-id");
         var unitName = dom.attr("unit-name");
         var unitTitle = "";
         dom.children("div.metadata")
            .children("span.metadata")
            .each(function() {
             if($(this).find('span.metadata-title').length > 0){
                unitTitle += $(this).find('span.metadata-title').text();
                unitTitle +=": ";
             }
             unitTitle += $(this).find('span.metadata-value').text();
         })
         var html = "";
         if (unitName != "sentence") {
             html += '<ul class="contents-listing" unit-id="'+unitId+'" unit-name="'+unitName+'">';
             html += '<li>';
             html += '<span class="unit-title">'+unitTitle+'</span>';
             var me = this;
             dom.children('div.unit').each(function() {
                 html += me.makeSubUnitsHTML($(this));
             })
             html += '</li>';
             html += '</ul>'
         }
         return html;
     }
});
