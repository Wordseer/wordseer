/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.barchart.BarChart', {
    extend:'Ext.Component',
    requires:[
        'WordSeer.view.wordmenu.WordMenu',
    ],
    alias:'widget.bar-chart',
    autoScroll: true,
    statics:{
        maxSize:20,
        minSize:0,
        fontSize:10,
        width:250,
        height:250
    },
    listeners:{
        afterrender:function(){
            this.container = this.getEl().dom;
            $(this.container).addClass('bar-chart-container');
            this.containerID = 'bar-chart-container-'+$('.bar-chart-container').length
            $(this.container).addClass(this.containerID);
            this.clickValues = [];
            this.clickData = {};
            this.baseInfo = {};
            this.allowHoverActions = true;
        }
    },
    drawData:function(data, maxValue, expand, isFilter){
        
        var me = this;
        this.data.forEach(function(datum){
            me.baseInfo[datum.name] = datum 
        });
        var margin, width, height, fontSize, 
        format, x_scale, y_scale, xAxis, yAxis, svg, bar, names, info;
        margin = {top: 20, right: 20, bottom: 20, left: 70};
        if(!isFilter){// drawing a new graph
            me.names = [];
            me.info = {};
            data.forEach(function(datum){
                me.names.push(datum.name);
                me.info[datum.name] = datum;
            })
            me.setWidth(this.self.width);
            var my_width = me.getWidth() == 0? this.self.width : me.getWidth();
            var my_height = me.getHeight() == 0? this.self.height : me.getHeight();
            width = my_width - margin.right - margin.left;
            height = Math.max(250, 12*this.names.length) - margin.top - margin.bottom;	
            me.x_scale = d3.scale.linear()
                .range([0, width]);        
            me.y_scale = d3.scale.ordinal()
                .rangeRoundBands([0, height], .3);
            me.x_scale.domain([0, maxValue]);
            me.y_scale.domain(me.names);
    	    me.xAxis = d3.svg.axis()
                .scale(me.x_scale)
                .orient("top")
                .ticks(Math.min(maxValue, 5))
                .tickFormat(d3.format('d'))
                .tickSize(-height, 0, 0);
            me.yAxis = d3.svg.axis()
                .scale(me.y_scale)
                .orient("left")
                .tickSize(0);
            $(me.container).html(""); // remove previous graph
            names = me.names;
            info = me.info;
            x_scale = me.x_scale;
            y_scale = me.y_scale;
            xAxis = me.xAxis;
            yAxis = me.yAxis;   
            fontSize = me.self.fontSize;
            format = d3.format("d");           
            svg = d3.select("."+me.containerID)
                .append("svg")
                .attr("width", width + margin.right + margin.left)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                    .attr("class", "svg")
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
            bar = svg.selectAll("g.bar")
                 .data(names)
                .enter().append("g")
                  .classed('bar', true)
                  .attr("transform", function(name) { 
                      return "translate(0," + y_scale(name) + ")"; 
                });
            //need enough data points      
            if(data.length > me.self.minSize || !expand){
                bar.append("rect")
                     .attr("class", "outline")
                     .attr("width", function(name) { return x_scale(info[name].value); })
                     .attr("height", y_scale.rangeBand());
                bar.append("rect")
                      .attr("class", "fill")
                      .attr("width", function(name) { return x_scale(info[name].value); })
                      .attr("height", y_scale.rangeBand());
                bar.append('text')
                     .attr("class", "value")
                     .attr("x", function(name){return x_scale(info[name].value)+10;})
                     .attr("y", y_scale.rangeBand()/2)
                     .attr("dx", -3)
                     .attr("dy", "0.35em")
                     .attr("color", "black")
                     .attr('text-anchor', "start")
                     .text(function(name){return info[name].value});
                 
                bar.on('mouseout', function(name){
                    d3.select(this)
                      .classed('hovered', false)
                    if(me.allowHoverActions){
                        me.filterOtherChart(name, this, 'hover');
                    }
                   })
                  .on('mouseover', function(name){
                      d3.select(this).classed('hovered', true);
                      if(me.allowHoverActions){
                          me.filterOtherChart(name, this, 'hover');
                      }
                  })
                  .on('click', function(name){
                      me.processClick(name, this);
                  });
          var xAxisGroup = svg.append("g")
              .attr("class", "x axis")
              .call(xAxis);

          var yAxisGroup = svg.append("g")
              .attr("class", "y axis")
              .call(yAxis);

          yAxisGroup.selectAll('text')
              .on('mouseover', function(){
                  d3.select(this).classed('menu-word', true);
                  $(this).css('cursor', 'pointer');
              })
              .on('mouseout', function(){
                  d3.select(this).classed('menu-word', false);
              })
              .on('click', function(name, i){
                  var word = Ext.create('WordSeer.model.WordModel', {
                      word:name,
                      class:'word',
                  });
                  var menu = Ext.widget('wordmenu', 
                      {
                        current:word,
                        shownBy: $(this),
                      });
                  menu.showBy(this);
                  $(this).addClass('menu-word'); 
              })
          this.show();
      	    }else{
      	        this.hide();
      	    }
        } else {
            info = me.info;
            keys(info).forEach(function(key){
                info[key] = {value:0};
            })
            data.forEach(function(datum){
                me.info[datum.name] = datum;
            })
            names = me.names;
            x = this.x_scale;
            // transition all the new
            svg = d3.select("."+this.containerID)
                .select('svg')
                .select('g.svg');
            text = svg.selectAll('g.bar text');
            text.text(function(name){
                    return info[name].value;
                });
            rects = svg.selectAll("g.bar rect.fill");
            rects.transition()
                .duration(500)
                .delay(function(name, i){return (i%names.length)*10;})
                .attr("width", function(name){return x(info[name].value);});
        }

        // Create the link to download data.
        this.makeDownloadLink(data);
    },
    filterOtherChart:function(name, item, eventType){
        var me = this;
        var other = me.otherChart;
        if(me.filterValue == name){
            // un-filter
            me.filterValue = '';
            me.isFiltered = false;
            // the other graph was also filtered, so
            // remove the filters
            other.isFiltered = false;
            other.filterValue = '';
            other.drawData(other.data,other.max,true, true);
        }else{
            // filters
            me.filterValue = name;
            me.isFiltered = true;
            if(eventType == "click"){
                d3.select(item).classed('clicked', true, true);
            }
            var d = me.info[name];
            if(!other.isFiltered){
                other.drawData(d.children,other.max,true, true)
                other.show();
            }
        }
    },
    processClick:function(name, item){
        var me = this;
        var other = me.otherChart;
        if(me.clickValues.contains(name)){
            // un-click
            me.clickValues.remove(name)
            d3.select(item).classed('clicked', false);
        }else{
            d3.select(item).classed('clicked', true);
            me.clickValues.push(name)
        }
        if(me.clickValues.length > 0){
            me.allowHoverActions = false;
            me.clickData = {};
            me.clickValues.forEach(function(name){
                    var barData = me.baseInfo[name].children;
                    barData.forEach(function(datum){
                        var name = datum.name;
                        if(!me.clickData.hasOwnProperty(name)){
                            me.clickData[name] = {name:name, value:0, children:[]};
                        }
                        me.clickData[name].value += datum.value    
                    })
            })
            if(!other.isFiltered){
                var dataList = [];
                keys(me.clickData).forEach(function(key){
                    dataList.push(me.clickData[key]);
                })
                other.drawData(dataList,other.max,true, true)
                other.show();
            }
        }else{
            me.allowHoverActions = true;
            other.isFiltered = false;
            other.filterValue = '';
            other.drawData(other.data,other.max,true, true); 
        }
        this.up().fireEvent('chartsFiltered');
    },

    makeDownloadLink: function(data) {
      var context = "";
      var widget = this.up('widget');
      if (widget) {
        var formValues = widget.getFormValues();
        var text = formValues.toText();
        if (text.length > 0) {
          context = " for " + text;
        }
      }

      var file_data = new goog.string.StringBuffer();
      file_data.append("Word\tCount\n");
      for (var i = 0; i < data.length; i++) {
        file_data.append(data[i].name+"\t"+data[i].value+"\n");
      }

      var data_url = "data:application/octet-stream," 
      + escape(file_data.toString());

      $(this.getEl().dom).find("a.download").remove();
      $(this.getEl().dom)
        .prepend("<a class='download' download='" + (getInstance() +
          " grammatical search results " + context)
          + "' href='" +data_url + "'>data</a>");
      $(this.getEl().dom).find("a.download").css("padding-left", "70px")
    }
    
})