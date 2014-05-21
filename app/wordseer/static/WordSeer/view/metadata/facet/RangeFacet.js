/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** Represents a numerical metadata category that the user selects as a range.
*/
Ext.define('WordSeer.view.metadata.facet.RangeFacet',{
    extend:'WordSeer.view.box.DataBox',
    alias:'widget.rangefacet',
    config: {
        /**
        @cfg {WordSeer.model.MetadataModel} info The MetadataModel representing
        the information for this facet.
        */
        info:[],

        /**
        @cfg {String} name The name of the facet.
        */
        name:"",

        /**
        @cfg {Number} max The maximum value of the numbers in the range.
        */
        max: 0,

        /**
        @cfg {Number} min The maximum value of the numbers in the range.
        */
        min: 0,

        /**
        @cfg {Number} total The total number of units matched.
        */
        total: 0,

        /**
        @cfg {String} type The type of values in this facet, either "number"
        or "date".
        */
        type: "number",

        collapsible: false,
    },

    constructor: function(cfg) {
      this.callParent(arguments);
      this.autoEl.cls = "range-facet";
      if (this.collapsible) { // If this is part of a metadata display
        this.autoEl.children[0].children.splice(0, 0, {
          tag: 'span',
          cls: 'action-button-toggle-expand action-button-toggle'
        });
        this.autoEl.children[0].children[1].tag = 'span';
        this.autoEl.children[0].children[1].cls = 'metadata-category';
        this.collapsed = true;
      } else {
        this.collapsed = false;
      }
      var chart = this.autoEl.children.filter(function(x){
        return x.cls == 'databox-body';})[0];
      chart.cls += " chart";
      chart.cls += this.collapsed? " collapsed " : "";
      chart.children = [
        {
          tag: 'div',
          cls:'title'
        }
      ];
    },
    minHeight: 90,
    width: '250',
    initComponent:function() {
        this.initialize();
        /** @event filter Fired when the user submits a filter.
        @param {WordSeer.view.metadata.facet.RangeFacet} range_view the filtered
        view.
        @param {String} range_start The start of the filter range.
        @param {String} range_end The end of the filter range.
        */
        this.addEvents('filter');

        this.callParent(arguments);
    },

    initialize: function() {
        var fields =  [
                {name:'value', type:'auto', defaultValue:0},
                {name: 'count', type: 'int', defaultValue:0},
                {name: 'propertyName', type:'string', defaultValue: ''},
                {name: 'displayName', type:'string', defaultValue: ''},
        ];
        var me = this;
        me.type = me.getInfo().get('type');
        me.parser = function(x){
          if ((x+"").indexOf(".") == -1) {
            return parseInt(x);
          } else {
            return parseFloat(x);
          }
        };
        me.formatter = function(x){
          var formatted = x + "";
          if (formatted.length > 4) {
            return x.toPrecision(4);
          } else {
            return formatted;
          }
        };
        if (me.getInfo().get('type').search("date_") == 0) {
            me.type = "date";
            var format = me.getInfo().get('type').substring(5);
            me.format = d3.time.format(format);
            me.parser = function(x){return me.format.parse(x);};
            me.formatter = function(x){return me.format(new Date(x));};
            fields[0].type = 'date'
        }
        this.children = this.getInfo().childNodes.map(
          function(c) {return c.raw;});
        this.children.forEach(function(child) {
          child.value = me.parser(child.text+"");
        });
        this.store = new Ext.data.Store({
            fields: fields,
            data: this.children
        });

        this.max = this.store.max('value');
        this.selectionMax = this.max;
        this.min = this.store.min('value');
        this.selectionMin = this.min;
        this.total = this.getInfo().get('count');
      },

    /** Draws a range slider and sparkline view for this metadata facet.
    */
    draw: function() {
      var me = this;
      if (me.collapsible) {
        me.addCollapseBehavior();
      }
      if (me.getEl() && me.getEl().dom && !me.chart_rendered) {
          me.chart_rendered = true;
          var canvas = d3.select(me.getEl().down('div.chart').dom);
          var svg_width = me.getWidth()*0.8;
          var svg_height = 30;
          x_scale = d3.scale.linear;
          if (me.type == "date") {
          	x_scale = d3.time.scale
          }
          me.chart = me.barChart(me)
          	.data(me.children)
          	.x(x_scale()
          		.domain([me.min, me.max])
          		.rangeRound([0, svg_width*0.9]))
          	.y(d3.scale.linear()
          		.domain([0, me.getStore().max('count')])
          		.range([svg_height, 0]))

          var renderChart = function(){
          	me.chart(canvas);
          }

          canvas.data([me.chart])
  	      .each(function(chart) {
  	      	chart.on("brush", renderChart)
  	      	.on("brushend", renderChart);
  	      });

  	    renderChart();
      }
    },

    barChart: function(panel) {

        var margin = {top: 10, right: 20, bottom: 20, left: 30},
            x,
            y = d3.scale.linear().range([100, 0]),
            id = Ext.id(),
            axis = d3.svg.axis().orient("bottom")
            	.tickFormat(panel.formatter)
            	.tickSubdivide(10),
            yaxis = d3.svg.axis()
            	.orient("left")
            	.tickSubdivide(2)
            	.tickFormat(function(y){return parseInt(y)+"";}),
            brush = d3.svg.brush(),
            brushDirty,
            data,
            max_value,
            round;

        function chart(div) {
				var width = x.range()[1]+5,
				height = y.range()[0];

				y.domain([0, panel.getStore().max('count')]);

				div.each(function() {
				var div = d3.select(this),
				g = div.select("g");

				// Create the skeletal chart. Add the title
				if (g.empty()) {
					div.select('.title').append("span")
					  .attr("class", "reset")
					  .text("reset")
					  .style("display", "none")
					  .on("click", function() {
					    panel.chart.filter(null);
					    panel.chart(div);
					  });

					div.select('.title').append("span")
					  .attr("class", "reset filter")
					  .text("filter")
					  .style("display", "none")
					  .on("click", function() {
					  	var extent = brush.extent()
					  	console.log(extent);
					    panel.fireEvent("filter",
					    	panel,
					    	panel.formatter(extent[0]),
					    	panel.formatter(extent[1]))
					  });

					div.select('.title').append("span")
					    .attr("class", "range-display")
					    .text("filter");

					g = div.append("svg")
					  .attr("width", width + margin.left + margin.right)
					  .attr("height", height + margin.top + margin.bottom)
					.append("g")
					  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

					g.append("clipPath")
					  .attr("id", "clip-" + id)
					.append("rect")
					  .attr("width", width)
					  .attr("height", height);

					g.selectAll(".bar")
					  .data(["background", "foreground"])
					.enter().append("path")
					  .attr("class", function(d) { return d + " bar"; })
					  .datum(data);

					g.selectAll(".foreground.bar")
					  .attr("clip-path", "url(#clip-" + id + ")");

					g.append("g")
					  .attr("class", "axis")
					  .attr("transform", "translate(0," + height + ")")
					  .call(axis);

					  g.append("g")
					    .attr("class", "axis")
					    .attr("transform", "translate(-3, 0)")
					    .call(yaxis);

					// Initialize the brush component with pretty resize handles.
					var gBrush = g.append("g").attr("class", "brush").call(brush);
					gBrush.selectAll("rect").attr("height", height);
					gBrush.selectAll(".resize").append("path").attr("d", resizePath);
	            }

	            // Only redraw the brush if set externally.
	            if (brushDirty) {
	              brushDirty = false;
	              g.selectAll(".brush").call(brush);
	              div.selectAll(".databox-header span").style(
	              	"display", brush.empty() ? "none" : null);
	              if (brush.empty()) {
	                g.selectAll("#clip-" + id + " rect")
	                    .attr("x", 0)
	                    .attr("width", width);
	              } else {
	                var extent = brush.extent();
	                g.selectAll("#clip-" + id + " rect")
	                    .attr("x", x(extent[0]))
	                    .attr("width", x(extent[1]) - x(extent[0]));
	              }
            	}

            g.selectAll(".bar").attr("d", barPath);
          });

          function barPath(data) {
	            var path = [],
	                i = -1,
	                d;
	            while (++i < data.length) {
	              d = data[i];
	              path.push("M", x(d.value)+2, ",", height,
	              	"V", y(d.count), "h0V", height);
	            }
	            return path.join("");
          }

          function resizePath(d) {
            var e = +(d == "e"),
                x = e ? 1 : -1,
                y = height / 3;
            return "M" + (.5 * x) + "," + y
                + "A6,6 0 0 " + e + " " + (6.5 * x) + "," + (y + 6)
                + "V" + (2 * y - 6)
                + "A6,6 0 0 " + e + " " + (.5 * x) + "," + (2 * y)
                + "Z"
                + "M" + (2.5 * x) + "," + (y + 8)
                + "V" + (2 * y - 8)
                + "M" + (4.5 * x) + "," + (y + 8)
                + "V" + (2 * y - 8);
          }
        }

        brush.on("brushstart.chart", function() {
          var div = d3.select(this.parentNode.parentNode.parentNode);
          	div.selectAll(".title span").style("display", null);
        });

        brush.on("brush.chart", function() {
          var g = d3.select(this.parentNode),
              extent = brush.extent();
          if (round) g.select(".brush")
              .call(brush.extent(extent = extent.map(round)))
            .selectAll(".resize")
              .style("display", null);
          g.select("#clip-" + id + " rect")
              .attr("x", x(extent[0]))
              .attr("width", x(extent[1]) - x(extent[0]));
          var div = d3.select(this.parentNode.parentNode.parentNode);
          div.select(".range-display")
            .text((panel.formatter(extent[0]) + " -- "
            	+ panel.formatter(extent[1])));

        });

        brush.on("brushend.chart", function() {
          var div = d3.select(this.parentNode.parentNode.parentNode);
          if (brush.empty()) {
            //div.selectAll("span").style("display", "none");
            div.select(".range-display").style("display", "none");
            div.select("#clip-" + id + " rect")
                .attr("x", null).attr("width", "100%");
            panel.setTotal(0);
          } else {
            var extent = brush.extent();
            var min = panel.type == "date"? new Date(extent[0]): extent[0];
            var max = panel.type == "date"? new Date(extent[1]): extent[1];
            var items = panel.children;
            var count = 0;
            items.forEach(function(item) {
            		if(item.value >= min && item.value <= max) {
            			count += parseInt(item.count);
            		}
            	});
            var old_text = div.select(".range-display").text();
            div.select(".range-display").text((old_text +  " (" + count + ")"));
            panel.setTotal(count);
          }
        });

        chart.margin = function(_) {
          if (!arguments.length) return margin;
          margin = _;
          return chart;
        };

        chart.x = function(_) {
          if (!arguments.length) return x;
          x = _;
          axis.scale(x);
          axis.tickValues([x.domain()[0], x.domain()[1]]);
          brush.x(x);
          brush.extent([x.domain()[0], x.domain()[1]]);
          return chart;
        };

        chart.y = function(_) {
          if (!arguments.length) return y;
          y = _;
          yaxis.scale(y);
          yaxis.tickValues([y.domain()[0], y.domain()[1]])
          return chart;
        };

        chart.filter = function(_) {
          if (_) {
            brush.extent(_);
          } else {
            brush.clear();
          }
          brushDirty = true;
          return chart;
        };

        chart.data = function(_) {
          if (!arguments.length) return data;
          data = _;
          return chart;
        };

        chart.round = function(_) {
          if (!arguments.length) return round;
          round = _;
          return chart;
        };

        return d3.rebind(chart, brush, "on");
  },

  /**
  Binds events to the collapse/expand buttons
  */
  addCollapseBehavior: function() {
    var me = this;
    var button = me.getEl().down('.action-button-toggle');
    if (button) {
      button.on('click', function(event) {
        if (me.collapsed) {
          me.getEl().down('div.chart').removeCls('collapsed');
          button.addCls('collapse')
        } else {
          me.getEl().down('div.chart').addCls('collapsed');
          button.removeCls('collapse')
        }
        me.collapsed = !me.collapsed;
      })
    }
  }
})
