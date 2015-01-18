/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */
/** The controller for the WordFrequencies.
http://trifacta.github.io/vega/
*/
Ext.define('WordSeer.controller.WordFrequenciesController', {
	extend: 'Ext.app.Controller',
	views: [
		'widget.WordFrequenciesWidget',
		'visualize.wordfrequencies.WordFrequencies',
	],
	init:function() {
//		console.log('Word Frequencies Controller Initialized');
		this.control({
			'word-frequencies': {
				'search': this.requestWordFrequenciesData,
				'draw': this.makeWordFrequencies,
			},
			'word-frequencies  checkbox[name=stacked]': {
				'change': this.change,
			},
			'word-frequencies  checkbox[name=normalized]': {
				'change': this.changeNormalized,
			},
			'word-frequencies  checkbox[name=labels]': {
				'change': this.toggleLabels,
			},
			'word-frequencies checkbox[action=hide-show-chart]': {
				'change': this.hideShowChart,
			},
			'word-frequencies  combobox': {
				'change': this.changeTopN,
			}
		});
	},

	/** Hides or shows the chart corresponding to the clicked-on checkbox.
	@param {Ext.form.field.Checkbox} The checkbox that was clicked.
	*/
	hideShowChart: function(checkbox) {
		var shown = checkbox.getValue();
		var title = checkbox.itemId;
		var chart = $(checkbox.up('word-frequencies').getComponent('canvas')
			.getEl().dom).find("#"+title);
		if (shown) {
			chart.fadeIn();
		} else {
			chart.fadeOut();
		}
	},

	/** Changes how many bars are displayed in ordinal charts. If anything
	other than "all" is selected, only the top N categories (by number of
	matches) are shown.
	@param {Ext.form.field.Combobox} combobox The "top N" combobox
	*/
	changeTopN: function(combobox) {
//		console.log("changed");
	  	var value = combobox.getValue();
	  	var panel = combobox.up('word-frequencies');
	  	panel.top_n = value;
	  	this.draw(panel.data, panel);
	},

	/** Changes the view from normalized to un-normalized.
	*/
	changeNormalized: function(checkbox) {
		var panel = checkbox.up('word-frequencies');
		if (panel.charts.length > 0) {
			this.renderAll(panel);
			var stacked_checkbox = panel.down('checkbox[name=stacked]');
			this.change(stacked_checkbox);
		}
	},

	/** Shows and hides the labels.
	*/
	toggleLabels: function(checkbox) {
		var panel = checkbox.up('word-frequencies');
		if (panel.charts.length > 0) {
			var value = checkbox.getValue();
			if (value) {
				$(panel.getEl().dom).find("text.value").show();
			} else {
				$(panel.getEl().dom).find("text.value").hide();
			}
		}
	},

	/** Changes the view from grouped to stacked
	*/
	change: function(checkbox) {
	  if (checkbox.getValue()) { // "stacked" is checked
		checkbox.up('word-frequencies').charts.forEach(function(chart){
			chart.stacked = true;
			chart.transitionStacked()
		})
	  } else {
		checkbox.up('word-frequencies').charts.forEach(function(chart){
			chart.stacked = false;
			chart.transitionGrouped()
		})
	  }
	},

	/** Fetches WordFrequencies data from the server in response to a search request.
	When the server returns the data, calls the draw code.

	@param {WordSeer.model.FormValues} formValues a
	{@link WordSeer.controll.SeachController formValues} object.
	@param {WordSeer.view.visualize.wordfrequencies.WordFrequencies}
	word_frequencies_panel The view into which the WordFrequencies should be
	rendered.
	*/
	requestWordFrequenciesData: function(formValues, word_frequencies_panel) {
//		console.log("requested word frequencies data");
		word_frequencies_panel.getEl().mask('loading');
		params = formValues.serialize();
		Ext.Ajax.request({
		    url: ws_project_path + project_id +  '/metadata_frequencies/',
		    method:'GET',
		    disableCaching: false,
		    timeout: 900000,
		    params: params,
		    scope:this,
		    success:function(response){
		        var data  = Ext.decode(response.responseText)
		        word_frequencies_panel.data = data;
		        this.draw(data, word_frequencies_panel);
            	if (word_frequencies_panel.getEl()){
        	    	word_frequencies_panel.getEl().unmask();
        	    }
		    },
		    reset:function(response) {
		    	if (word_frequencies_panel.getEl()){
			    	word_frequencies_panel.getEl().unmask();
			    }
		    },
		    failure: function(response) {
		    	if (word_frequencies_panel.getEl()) {
			    	word_frequencies_panel.getEl().unmask();
		    	}
		    	console.log("request to bar-charts failed.");
		    }
		})
	},

	/** A pre-processing step necessary for correctly using d3's stacked area
	layout function. Given a list of lists, makes sure the lists have the same
	number of key-value pairs (inserting 0 values for values where necessary),
	and sorts the lists so that the keys are all in the same order.

	@param {Object} data A list of lists of {key:< >, value: <count>} pairs for
	the frequencies of words across different metadata categories (the key
	values).
	*/
	addMissingStackKeys: function(data) {
		function contains(array, key) {
			if(key instanceof Date) {
				for (var i = 0; i < array.length; i++) {
					if (array[i]) {
						if (array[i].getTime() == key.getTime()) {
							return true;
						}
					}
				}
				return false;
			} else {
				return array.indexOf(key) != -1;
			}
		};
		var all_keys = [];
		var new_data = [];
		for (var i = 0; i < data.length; i++) {
			var values = data[i];
			var keys = values.map(function(d){
				return d.key;
			})
			for (var k = 0; k < keys.length; k++) {
				var key = keys[k];
				if (!contains(all_keys, key)) {
					all_keys.push(key)
				}
			}
		}
		for (var i = 0; i < data.length; i++ ) {
			var values = data[i];
			var keys = values.map(function(d) {
				return d.key;
			})
			for (var j = 0; j < all_keys.length; j++) {
				var key = all_keys[j];
				if (!contains(keys, key)) {
					values.push({
						key: key,
						value: 0,
						x: key,
						y: 0
					})
				}

			}
			values.sort(function(a, b) {
				if (a.key < b.key) {
					return -1;
				} else if (a.key > b.key) {
					return +1;
				} else {
					return 0;
				}
			})
			new_data.push(values);
		}
		return data;
	},

	/** Creates a word frequency chart of the given type (either "string", which
	results in a bar chart,  or "number", which gives a scatter plot with an
	area chart).

	@param {String} type The type of the metadata category for which the word
	frequencies are being drawn.
	*/
	barChart: function(type, panel, controller, width, height, padding) {
		var	area,
			area_fn, // area path element
			backdrop, // backdrop bars or points
			bandWidth, // the total width of the band of bars in the bar chart
			bg_area, // the backdrop area path element
			bg_color, // the color scale for the backdrop
			bg_text, // the labels on the points or bars
			brush = d3.svg.brush(), // the brush for the numerical axes
			brushDirty = false, // status for the brush
			color, // the color scale for the different searches
			dimensions, // the data points for the different searches
			draw_area = true, // whether or not to draw a stacked area graph instead of a bar chart
			foreground = d3.selectAll("circle.foreground.freq-line"), // foreground bars or points
			format,// the formatter that takes in key values and outputs strings
			fg_area, // the foreground area path element
			groups, // the grouped data points for the different searches.
			id = Ext.id(), // the identifier of this chart
			layers, // the grouped data points
			legend, // the names of the searches for each color
			n, // number of layers
			normalized,
			m, // number of samples per layer
			radius, // the radius of the dots (in the scatterplot case)
			round,
			selected, // the selected item, for categorical scales.
			shape = (type == "string" && draw_area)? "rect": "circle",  // for categorical vs. numerical axes
			stack = d3.layout.stack(),
			stacked, // the data points augmented with the stacked layout
			title, // The title of the chart.
			total_counts, // The total number of units that match each category, for normalization
			x,  // the x axis scale function
			xAxis = d3.svg.axis().orient("bottom"), // the rendered x axis
			x_attr = (type == "string" || !draw_area)? "x": "cx", // the attribute that determines the x-position of bars or points
			y_axis, // the rendered y axis.
			yAxis = d3.svg.axis().orient("left")
            	.tickSubdivide(2),
        	y_attr = (type == "string") ? "y": "cy", // the attribute that determines the y-position of bars or points
			yGroupMax, // the max y value in the grouped configuration
			yStackMax; // the max y value in the stacked configuration


		var context = "";
		var widget = panel.up('widget');
		if (widget) {
			var formValues = widget.getFormValues();
			var text = formValues.toText();
			if (text.length > 0) {
				context = " for " + text;
			}
		}

		function chart(div) {
			//try {

					color = COLOR_SCALE;
					bg_color = function(i) {
						var c = d3.rgb(color[i]);
						var average = (0.21*c.r + 0.71*c.g + 0.07*c.b);
						return d3.rgb(average, average, average);
					};

					// Calculate the y values for the data, depending on
					// whether the data is normalized. Then also calculate
					// the max and min values of y, to set the domain
					// of the y axis.
					var max_count = 0;
					normalized = panel.down('checkbox[name=normalized]')
						.getValue();
					yAxis.tickFormat(function(y){
							var small_format = d3.format(".2%");
							return normalized?
							small_format(y) :parseInt(y)+"";})
					var data = d3.range(groups.length).map(function(i) {
						this_data = [];
						var group = groups[i];
						if (group.top(1).length > 0) {
							max_count = (group.top(1)[0].value.length > max_count) ?
								group.top(1)[0].value.length : max_count;
							var raw_data =  type == "string" && panel.top_n != "all" ?
							groups[i].top(panel.top_n) : groups[i].all();
							raw_data.forEach(function(d) {
								if (typeof(d.key) != "undefined") {
									this_data.push(d);
								}
							})
							this_data.forEach(function(d){
								var total = total_counts[format(d.key, title)];
								var value = d.value.length;
								d.x = d.key;
								d.total = total;
								d.mean = total > 0 ? (value/total): 0
								d.y = normalized ? d.mean : value;
								d.y0 = 0;
								d.stdev = Math.sqrt(
									d3.mean(
									d3.map(
										keys(d.value.statistics
												.random_partition),
									function(key) {
										var p = d.value.statistics
											.random_partition[key];
										return Math.pow(
											d.mean - (p.count/p.total), 2);
									})));
								d.stdev = normalized? d.stdev : d.stdev*total;
							});
						}
						return this_data;
					})
					data = controller.addMissingStackKeys(data);

					// Calculate the domain of the input data after adding
					// all the missing keys and removing undefined values.
					if (type == "string" && data.length > 0) {
						var domain = data[0].map(function(d){return d.key});
						domain.sort();
						x.domain(domain);
					}
					layers = stack(data);
					n = data.length;
					if (n > 0) {
						m = data[0].length;
					}

					// Calulate what the maximum y values would be in the
					// grouped and stacked cases.
					yGroupMax = d3.max(layers, function(layer) {
						return d3.max(layer, function(d) { return d.y; }); });
					yStackMax = d3.max(layers, function(layer) {
						return d3.max(layer, function(d) { return d.y0 + d.y; }); });

					// If the chart is grouped, need to set the width of the
					// individual bars to fit intothe existing band width.
					// the bandWidth variable controls this.
					if (type == "string" || !draw_area) {
						bandWidth = x.rangeBand();
					} else {
						if(data.length > 0) {
							var num_keys = data[0].length;
							var total_band_width = width/num_keys;
							bandWidth = total_band_width*(1-padding);
						}
					}
					bandWidth = Math.max(bandWidth, 1);

					area_fn = d3.svg.area()
						.x(function(d) {return x(d.x);})
						.y0(function(d) { return stacked? y(d.y0): height;})
						.y1(function(d) {return stacked? y(d.y + d.y0): y(d.y);});

					area = function(d) {
						var path = area_fn(d);
						if (path) {
							return path.replace(/NaN/g, "0");
						} else {
							return null;
						}
					}

					div.forEach(function(dom) {
						var div = d3.select(dom),
							g = div.select("g");

						// Create the skeletal chart.
						if (g.empty()) {
							div.select(".title").append("span")
									.attr("class", "reset")
									.text("reset")
									.style("display", "none")
									.on("click", function() {
										$(this).hide();
										chart.filter();
										controller.renderAll(panel);
									});
							div.select(".title").append("a")
									.attr("class", "reset download")
									.text("data")
									.attr("download", ("sentence counts across "
									 + title +  context + ".tsv"))
									.attr("href", "");

							g = div.append("svg")
									.attr("width", width + margin.left + margin.right)
									.attr("height", height + margin.top + margin.bottom)
								.append("g")
									.attr("transform", "translate(" + margin.left + ","
										+ margin.top + ")");


							g.append("clipPath")
									.attr("id", "clip-" + id)
								.append("rect")
									.attr("width", width)
									.attr("height", height);

							g.append("clipPath")
									.attr("id", "allclip-" + id)
								.append("rect")
									.attr("width", width)
									.attr("height", height);

							var graphs = g.selectAll(".freq")
									.data(["backdrop", "foreground"])
									.enter().append("g")
									.attr("class", function(d) { return d + " freq"; });

							foreground_layers = g.select('.foreground.freq')
									.selectAll(".layer")
									.data(layers)
									.enter().append("g")
									.attr("class", "layer")
									.style("fill", function(d, i) {
										return color[i];
									});

							foreground = foreground_layers.selectAll("g")
								.data(function(d) { return d; })
							  .enter().append("g")
								  .attr("x", function(d) { return x(d.x); })
								  .attr("y", function(d) {
								  	return y(d.y0 +d.y)
								  })
							  	.append(shape)
							  	.attr("class", function(d) {
							  		var c = "foreground freq-line";
							  		if (type == "string" || !draw_area) {
							  			c += " string";
							  		}
							  		return c;
							  	})
								.attr("r", radius)
								.style("cursor", "pointer")
								.attr("height", function(d) {return
								 	y(d.y0) - y(d.y)})
								.attr("width", bandWidth)
								.on("click", function(d) {
									var g = d3.select(this.parentNode.parentNode.parentNode.parentNode);
									if (selected == d) {
										var div = d3.select(this.parentNode.parentNode.parentNode);
										div.select(".title span.reset").style("display", "none");
										div.select("#clip-" + id + " rect")
										.attr("x", null).attr("width", "100%");
										dimensions.forEach(function(dimension) {
											dimension.filterAll();
										});
										selected = null;
									} else {
										var div = d3.select(
											this.parentNode.parentNode.parentNode
												.parentNode.parentNode);
										div.select(".title span.reset").style("display", null);
										selected = d;
										g.select("#clip-" + id + " rect")
												.attr("x", x(d.key))
												.attr("width", bandWidth);
										dimensions.forEach(function(dimension) {
											dimension.filter(d.key);
										});
									}
									controller.renderAll(panel);
								})
								.attr("clip-path", "url(#clip-" + id + ")");

							if (type != "string" && draw_area) {
								fg_area = foreground_layers.append("path")
									.attr("class", "area")
									.attr("d", area)
									.attr("clip-path", "url(#clip-" + id + ")");
							}

							backdrop_layers = g.select('.backdrop.freq')
									.selectAll(".layer")
									.data(layers)
									.enter().append("g")
									.attr("class", "layer")
									.style("fill", function(d, i) {
										return bg_color(i); });

							backdrop = backdrop_layers.selectAll(shape)
								.data(function(d) { return d; })
							  .enter().append(shape)
								.attr(x_attr, function(d) { return x(d.x); })
								.attr(y_attr, height)
								.attr("r", radius)
								.attr("width", bandWidth)
								.attr("height", 0)
								.attr("clip-path", "url(#allclip-" + id + ")");

							if (type != "string" && draw_area) {
								bg_area = backdrop_layers.append("path")
									.attr("class", "area")
									.attr("d", area)
									.attr("clip-path", "url(#allclip-" + id + ")");
							}

							bg_text = backdrop_layers.selectAll('text')
								 .data(function(d) {
								 	return d;})
								 .enter().append("text")
							     .attr("class", "value")
							     .attr("x", function(d){return x(d.x);})
							     .attr("y", height)
							     .style("font-size", "10px")
							     .style("fill", "#666")
							     .attr("transform",  "translate(2, -2)")
							     .attr('text-anchor', "start")
							     .text(function(d){
							     	var small_format = d3.format(".2%");
							     	if (d.y > 0) {
								     	if (d.y < 1 && d.y > 0) {
								     		return small_format(d.y);
								     	} else {
								     		return d.y
								     	}
							     	} else {
							     		return "";
							     	}
							     });

							g.append("g")
									.attr("class", "x axis")
									.attr("transform", "translate(0," + (height+radius) + ")")
									.call(xAxis);

							g.selectAll(".x.axis text")
								.style("text-anchor", "start")
								.attr("transform", "rotate(45 0,0)");

							g.append("g")
									.attr("transform", "translate(-3, 0)")
									.attr("class", "y axis");
							y_axis = g.select("g.y.axis");

							if (chart.type != "string") {
								// Initialize the brush component with pretty handles.
								var gBrush = g.append("g")
									.attr("class", "brush").call(brush);
								gBrush.selectAll("rect")
									.attr("height", height);
								gBrush.selectAll(".resize").append("path")
								.attr("d", resizePath);
							}
						}

						// //Rotate the text labels if normalized so that the values
						// //have more space (the decimal values have many digits)
						// if (normalized) {
						// 	g.selectAll("text.value")
						// 		.attr("transform",  function(d) {
						// 			return "translate(5, -2) rotate(-90 "+x(d.x)+",0)";
						// 		});
						// } else {
						// 	g.selectAll("text.value")
						// 		.attr("transform",  "translate(2, -2)");
						// }

						// Only redraw the brush if set externally.
						if (type != "string" && brushDirty) {
							brushDirty = false;
							g.selectAll(".brush").call(brush);
							div.select(".title a").style("display", brush.empty() ? "none" : null);
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

						} else if (type == "string" && selected == null) {
							g.selectAll("#clip-" + id + " rect")
									.attr("x", 0)
									.attr("width", width);
						}

						g.selectAll('path.axis')
							.style("stroke-width", "1");


						// Make the export data.
						var separator = "\t";
						var file_data = new goog.string.StringBuffer();
						file_data.append(title + "\t" + legend.join("\t") +"\n");
						if (layers.length > 0) {
							var keys = [];
							for (var i = 0; i < layers[0].length; i++) {
								var key = layers[0][i].x;
								if (key) {
									keys.push(key.toString());
								} else {
									keys.push("null")
								}
							}
							for (var i = 0; i < keys.length; i++) {
								var key = keys[i];
								var formatted = "null";
								if (key != "null") {
									formatted = format(key);
								}
								var values = [formatted];
								for (var j = 0; j < layers.length; j++) {
									values.push(layers[j][i].y);
								}
								file_data.append(values.join(separator) + "\n");
							}
						}
						var data_url = "data:application/octet-stream," +
							escape(file_data.toString());
						div.select(".title").select("a.download")
							.attr("href", data_url);

					});

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
				// } catch (err) {
				// 	//throw err;
				// 	console.log("Failed to make chart for "+ title);
				// 	console.log(err);
				// }
			}

		brush.on("brushstart.freq-chart", function() {
			var div = d3.select(this.parentNode.parentNode.parentNode);
			div.select(".title span").style("display", null);
		});

		brush.on("brush.freq-chart", function() {
			var g = d3.select(this.parentNode),
					extent = brush.extent();
			var visible_extent = extent.slice();
			if (round) g.select(".brush")
					.call(brush.extent(extent = extent.map(round)))
				.selectAll(".resize")
					.style("display", null);
			g.select("#clip-" + id + " rect")
					.attr("x", x(extent[0]))
					.attr("width", x(extent[1]) - x(extent[0]));
			dimensions.forEach(function(dimension){
				dimension.filterRange(extent);
			});
			controller.renderAll(panel);
		});

		brush.on("brushend.freq-chart", function() {
			if (brush.empty()) {
				var div = d3.select(this.parentNode.parentNode.parentNode);
				div.select(".title span").style("display", "none");
				div.select("#clip-" + id + " rect").attr("x", null).attr("width", "100%");
				dimensions.forEach(function(dimension) {
					dimension.filterAll();
				});
				controller.renderAll(panel);
			}
		});

		chart.type = type;
		chart.stacked = stacked;

		chart.transitionGrouped = function() {
			try {
					this.stacked = false;
					y.domain([0, yGroupMax]);
					yAxis.scale(y);
					y_axis.transition().call(yAxis);
					area = d3.svg.area()
						.x(function(d) {return x(d.x);})
						.y0(function(d) { return height;})
						.y1(function(d) {return y(d.y);});

					foreground.transition()
					  .attr(x_attr, function(d, i, j) {
					  	return (type == "string" || !draw_area ) ?
					  		x(d.x) + (bandWidth/n)*j : x(d.x)
					  })
					  .attr("width", bandWidth/n)
					  .attr(y_attr, function(d) {
					  	var total = y(d.y);
					  	return total;
					  })
					  .attr("height", function(d) { return height - y(d.y); });

					if (type != "string" && draw_area) {
						fg_area.transition().attr("d", area);
					}

					backdrop.transition()
						.attr(x_attr, function(d, i, j) {
					  	return (type == "string" || !draw_area ) ?
					  		x(d.x) + (bandWidth/n)*j : x(d.x)
					  	})
						.attr("width", bandWidth/n)
						.attr(y_attr, function(d) { return y(Math.max(0, d.y)); })
						.attr("height", function(d) {
							return height - y(d.y);
						});

					// Redraw the text labels
					bg_text.transition()
					.attr("transform",  function(d) {
								var base =  "translate(2, -2) ";
								if (normalized) {
									//base +=  "rotate(-90 "+x(d.x)+",0)";
								}
								return base
							})
					.text(function(d){
						var small_format = d3.format(".2%");
				     	if (d.y < 1 && d.y > 0) {
				     		return small_format(d.y);
				     	} else {
				     		return d.y
				     	}
				     	})
						.attr("y", function(d){return y(d.y)})
						.attr("x", function(d, i, j) {
					  	return (type == "string" || !draw_area ) ?
					  		x(d.x) + (bandWidth/n)*j : x(d.x)
					  });

					if (type != "string" && draw_area ){
						bg_area.transition().attr("d", area);
					}

				} catch (err){console.log(err)}};

		chart.transitionStacked = function() {
			//try{
					this.stacked = true;
					y.domain([0, yStackMax]);
					yAxis.scale(y);
					y_axis.transition().call(yAxis);
					area = d3.svg.area()
						.x(function(d) {return x(d.x);})
						.y0(function(d) { return y(d.y0);})
						.y1(function(d) {return y(d.y + d.y0);});

					foreground.transition()
					  .attr(y_attr, function(d) {
					  	var total =  y(d.y0 + d.y);
					  	return total;
					  })
					  .attr("width", bandWidth)
					  .attr("height", function(d) {
					  	var total = y(d.y0) - y(d.y0 + d.y);
					  	return total;
					  })
					  .attr(x_attr, function(d) { return x(d.x); });

					if (type != "string" && draw_area){
						fg_area.transition().attr("d", area);
					}

					backdrop.transition()
						.attr(y_attr, function(d) { return y(Math.max(0, d.y0 + d.y)); })
						.attr("height", function(d) {
							return (type ==  "string" || !draw_area) ? y(d.y0) - y(d.y0 + d.y):""; })
						.attr("width", (type== "string" || !draw_area) ? bandWidth:"")
						.attr(x_attr, function(d) { return x(d.x); });

					// Redraw the text labels
					bg_text.transition().text(function(d, i, j) {
							var value = ((n == j + 1) ? (d.y0 + d.y) : 0);
							var small_format = d3.format(".2%");
					     	if (value < 1 && value > 0) {
					     		return small_format(value);
					     	} else if (value > 0) {
					     		return value
					     	} else {
					     		return "";
					     	}
						})
						.attr("transform",  function(d) {
							var base =  "translate(2, -2) ";
							if (normalized) {
								//base +=  "rotate(-90 "+x(d.x)+",0)";
							}
							return base
						})
						.attr("y", function(d){return y(d.y0 + d.y)})
						.attr("x", function(d){return x(d.x)});

					if (type != "string" && draw_area){
						 bg_area.transition().attr("d", area);
					}
				//} catch(err){console.log(err)}
			};

		chart.margin = function(_) {
			if (!arguments.length) return margin;
			margin = _;
			return chart;
		};

		chart.total_counts = function(_) {
			if (!arguments.length) return total_counts;
			total_counts = _;
			return chart;
		};

		chart.normalized = function(_) {
			if (!arguments.length) return normalized;
			normalized = _;
			return chart;
		};

		chart.x = function(_) {
			if (!arguments.length) return x;
			x = _;
			brush.x(x);
			xAxis.scale(x);
			return chart;
		};

		chart.y = function(_) {
			if (!arguments.length) return y;
			y = _;
			yAxis.scale(y);
			return chart;
		};

		chart.yStackMax = function(_) {
			if (!arguments.length) return yStackMax;
			yStackMax = _;
			return chart;
		};

		chart.yGroupMax = function(_) {
			if (!arguments.length) return yGroupMax;
			yGroupMax = _;
			return chart;
		}

		chart.legend = function(_) {
			if (!arguments.length) return legend;
			legend = _;
			return chart;
		};

		chart.radius = function(_) {
			if (!arguments.length) return radius;
			radius = _;
			return chart;
		}

		chart.format = function(_) {
			if (!arguments.length) return format;
			format = _;
			if (typeof(format) == "string") {
				// Take into account format strings for dates.
				var formatter = d3.time.format(format);
				format = function (k) {
					return formatter(new Date(k))
				}
			}
			return chart;
		}

		chart.dimensions = function(_) {
			if (!arguments.length) return dimensions;
			dimensions = _;
			return chart;
		};

		chart.title = function(_) {
			if (!arguments.length) return title;
			title = _;
			return chart;
		};

		chart.filter = function(_) {
			if (_) {
				if (type != "string") {
				    brush.extent(_);
					dimensions.forEach(function(dim){
						dim.filter(_);
					});
					brushDirty = true;
				} else {
					dimensions.forEach(function(dim){
						dim.filterExact(_);
					});
				}
			} else {
				if (type != "string") {
					brush.clear();
					brushDirty = true;
				} else {
					selected = null;
				}
				dimensions.forEach(function(dim){
					dim.filterAll();
				});
			}
			return chart;
		};

		chart.groups = function(_) {
			if (!arguments.length) return groups;
			groups = _;
			return chart;
		};

		chart.round = function(_) {
			if (!arguments.length) return round;
			round = _;
			return chart;
		};

		if (type != "string") {
			return d3.rebind(chart, brush, "on");
		} else {
			return d3.rebind(chart, foreground, "on");
		}
	},

	/** Draws a WordFrequencies.
	@param {Object} data The data structure containing a list of lists, where
	each list contains sentence records, each with complete metadata, that match
	each search in the {@link WordSeer.model.FormValues#search} values.
	frequencies.
	@param {WordSeer.view.visualize.wordfrequencies.WordFrequencies} panel the
	view in which the wordfrequencies is currently being drawn.
	*/
	draw: function(data, panel) {
		/** Converts dates formatted as strings into Javascript Date objects.
		@param {Object} items A list of lits of sentence records matching the
		searches issued by the user.
		*/
		function reformat (items) {
			var reformatted = [];
			items.forEach(function(item) {
				var ok = true;
				for (property in item) {
					if (item.hasOwnProperty(property)) {
						if (property != "sentence_id"
							&& property != "document_id"
							&& property != "words") {
							var components = property.split("__");
							var type = components[0];
							if (type != "string") {
								var value = item[property];
								if (type == "number") {
									item[property] = value *1;
									formats[property] = function(x){return x};
								} else if (type.indexOf("date") >= 0) {
									var components = type.split("_");
									var format = components[1];
									if (!formats[property]) {
										formats[property] = format;
									}
									item[property] = d3.time.format(format).parse(value)
								}
								value = item[property];
								if (!domains.hasOwnProperty(property)
									|| domains[property].length == 0) {
									domains[property] = [value, value]
								}
								if (value < domains[property][0]) {
									domains[property][0] = value;
								}
								if (value > domains[property][1]) {
									domains[property][1] = value;
								}
							} else {
								formats[property] = function(x){return x};
								var value = item[property];
								if (property.indexOf("_set") != -1) {
									var store = null;
									if (property == "string__phrase_set") {
										store = 'PhraseSetListStore';
									} else if (property == "string__sentence_set") {
										store = 'SentenceSetStore';
									} else if (property == "string__document_set") {
										store = 'DocumentSetStore'
									}
									if (store) {
										var record = Ext.getStore(store).getById(
											parseInt(value));
										if (record) {
											value = record.get('text');
										} else {
											value = undefined;
										}
									}
									formats[property] = function(id, property) {
										var store = null;
										if (property) {
											if (property.indexOf("word") != -1) {
												store = 'PhraseSetListStore';
											} else if (property.indexOf("sentence") != -1) {
												store = 'SentenceSetStore';
											} else if (property.indexOf("document") != -1) {
												store = 'DocumentSetStore'
											}
										}
										if (!(parseInt(id)>0)) {
											return id;
										} else {
											if (store) {
												var record = Ext.getStore(store).getById(
													parseInt(id));
												if (record) {
													return record.get('text');
												}
											}
											return undefined;
										}
									};
									item[property] = value;
								}
								if (domains[property] == undefined) {
									domains[property] = [];
								}
								if(domains[property].indexOf(value) == -1) {
									domains[property].push(value);
								}
							}
							var value = item[property];
							if (value == undefined) {
									ok = false;
							}
						}
					}
				}
				if (ok) {
					reformatted.push(item);
				}
			})
			for (property in domains) {
				if (domains.hasOwnProperty(property)) {
					if(domains[property].length > 2) {
						domains[property].sort();
					}
				}
			}
			return reformatted;
		};

		var canvas = panel.getComponent('canvas');

		// Clear any previous charts.
		panel.charts = [];
		panel.chart_divs = [];
		$(panel.getEl().dom).find('div.freq-chart').remove()

		// Set the top_n value picker's visibility depending on the number of
		// data points


		var charts = panel.charts;
		var chart_height = 300;
		var chart_width = 500;
		var dimensions = {};
		var formats = {};
		var for_normalization = {};
		var controller = this;
		var domains = {};
		var groups = {};
		var legend = [];
		var margin = {top: 20, right: 10, bottom: 150, left: 50};
	    var height = chart_height - margin.top - margin.bottom;
		var width = chart_width - margin.left - margin.right;
		var padding = 0.1;
		var radius = 2;
		var sentence_properties = [];
		var max_num_points = 0;

		// Make the legend.
		var widget = panel.up(widget);
		if (widget) {
			var formValues = widget.formValues;
			if (formValues.search.length  > 0) {
				for (var i = 0; i < formValues.search.length; i++) {
					var fv = Ext.create('WordSeer.model.FormValues');
					fv.search.push(formValues.search[i]);
					legend.push(fv.toText());
				}
			}
		}

		// Re-format the data, pull out the sentence properties, and make
		// a crossfilter for each property for each set of search results.
		for (var index = 0; index < data.counts.length; index++) {
			raw_data = data.counts[index];
			var sentences = raw_data.sentences;
			var documents = raw_data.documents;
			var query = raw_data.query;

			var props = keys(data.for_normalization);
			sentence_properties = [];
			for (var i = 0; i < props.length; i++) {
				var count_data = data.for_normalization[props[i]];
				var property = count_data.type + "__" + props[i];
				if (sentence_properties.indexOf(property) == -1) {
					sentence_properties.push(property);
					domains[property] = [];
				}
			}
			sentences = reformat(sentences);

			// Get the normalizing counts i.e. sentence counts for that category
			// across the entire corpus.
			for (var i = 0; i < props.length; i++) {
				var count_data = data.for_normalization[props[i]];
				var property = count_data.type + "__" + props[i];
				if (domains[property].length > 0 || property.indexOf("string__") == -1){
					var total_counts = {};
					count_data.children.forEach(function(child) {
						total_counts[child.text] = parseInt(child.count);
					})
					for_normalization[property] = total_counts;
				}
			}

			var filtered_props = [];
			for (var i = 0; i < sentence_properties.length; i++) {
				var property = sentence_properties[i]
				if (domains[property].length > 0 || property.indexOf("string__") == -1) {
					if (filtered_props.indexOf(property) == -1) {
						filtered_props.push(property);
					}
				}
			}
			sentence_properties = filtered_props;



			// Create the crossfilter for the relevant dimensions and groups.
			var frequencies = crossfilter(sentences),
					all = frequencies.groupAll();

			var reduce_initial = function() {return {
					length:0,
					statistics:{
						groups:{},
						random_partition:{},
					}}};
			var reduce_add = function(p, v) {
				if (!p[v.sentence_id]) {
					p[v.sentence_id] = 1;
					p.length += 1;
				}
				return p
			}
			var reduce_remove = function(p, v) {
				if (p[v.sentence_id]) {
					delete p[v.sentence_id];
					p.length -= 1;
				}
				return p
			}
			for (var i = 0; i < sentence_properties.length; i++) {
				var property = sentence_properties[i];
				// Only include charts for categories present in the data.
				if (domains[property].length > 0 || property.indexOf("string__") == -1) {
					if (!dimensions.hasOwnProperty(property)) {
						dimensions[property] = [];
						groups[property] = [];
					}
					var dim = frequencies.dimension(function(d){
						return d[property];
					});
					dimensions[property].push(dim);

					var group = dim.group();
					group.reduce(reduce_add, reduce_remove, reduce_initial);
					groups[property].push(group);
					props.push(property);
				}
			}
		}

		// Instantiate the charts.
		for (var i = 0; i < sentence_properties.length; i++) {
			var property = sentence_properties[i];
			var title = property.split("__")[1];
			var type = property.split("__")[0];
			// Add a checkbox to hide and show this chart if it doesn't exist.
			if (!panel.getComponent('tbar').getComponent(title)) {
				panel.getComponent('tbar').add({
					xtype: 'checkbox',
					fieldLabel: title,
					labelAlign: 'right',
					labelWidth: (6*title.length)+15,
					labelPad: 2,
					itemId: title,
					action: 'hide-show-chart',
				})
				panel.getComponent('tbar').getComponent(title).setValue(
					!(title == "average_word_length" ||
						title == "sentence_length"));
			}

			var max_count = 0;
			var group_data = groups[property];
			if (type == "string" && panel.top_n != "all") {
				domains[property] = []
			}
			var data = d3.range(group_data.length).map(function(i) {
				var group = group_data[i];
				this_data = [];
				if (group.top(1).length > 0) {
					max_count = (group.top(1)[0].value.length > max_count) ?
						group.top(1)[0].value.length : max_count;
					var raw_data = (type == "string" && panel.top_n != "all") ?
						group_data[i].top(panel.top_n) : group_data[i].all();
					raw_data.forEach(function(d){
						if(typeof(d.key) != "undefined") {
							this_data.push(d);
						}
					})
					this_data.forEach(function(d){
						d.x = d.key;
						d.y = d.value.length;
						if (type == "string" && panel.top_n != "all" &&
							domains[property].indexOf(d.key) == -1) {
							domains[property].push(d.key)
						}
					});
				}
				return this_data;
			})
			if (type == "string" && panel.top_n != "all") {
				domains[property].sort();
			}
			data = this.addMissingStackKeys(data);
			var num_points = data[0].length;
			var max_num_points = type == "string" && (num_points > max_num_points) ?
				num_points : max_num_points;
			if (max_num_points > 20) {
				//panel.down('combobox').show();
			}
			var border_width = margin.left + margin.right;
			var w = Math.max(chart_width,
				(num_points * (type=="string"?20:5))) - border_width;
			var x = d3.scale.ordinal()
				.rangeRoundBands([0, w], padding)
				.domain(domains[property]);
			var draw_area = true;
			if (type != "string" && draw_area) {
				x = d3.scale.linear()
					.rangeRound([0, w])
					.domain(domains[property]);
				if (type.indexOf("date") != -1) {
					x = d3.time.scale()
						.rangeRound([0, w])
						.domain(domains[property]);
				}
			}

			$(canvas.getEl().dom).append(('<div id="'
				+ title +'" class="freq-chart"> <div class="title">' + title
				+ '</div></div>'));

			var shown = panel.getComponent('tbar').getComponent(title)
				.getValue();
			if (!shown) {
				$(canvas.getEl().dom).find("#"+title).hide();
			}

			var l = d3.layout.stack()(data);
			var ygm = d3.max(l, function(layer) {
				return d3.max(layer, function(d) { return d.y; }); });
			var yStackMax = d3.max(l, function(layer) {
				return d3.max(layer, function(d) { return d.y0 + d.y; }); });
			var chart = this.barChart(type, panel, this, w, height, padding)
					.dimensions(dimensions[property])
					.groups(groups[property])
					.format(formats[property])
					.margin(margin)
					.radius(radius)
					.title(title)
					.total_counts(for_normalization[property])
					.legend(legend)
					.x(x)
					.y(d3.scale.linear()
						.domain([0, yStackMax])
						.range([height, 0]))
					.yStackMax(yStackMax)
					.yGroupMax(ygm);
			chart.stacked = true;
			panel.charts.push(chart)
		}

		// Given our array of charts, which we assume are in the same order as the
		// .chart elements in the DOM, bind the charts to the DOM and render them.
		// We also listen to the chart's brush events to update the display.
		var controller = this;
		panel.chart_divs = d3.select(canvas.getEl().dom).selectAll(".freq-chart")
				.data(charts)
				.each(function(chart) {
					if(chart.on) {
						if (chart.type == "range") {
							chart.on("brush", function(){
								controller.renderAll(panel)
							}).on("brushend", function(){
								controller.renderAll(panel)
							});
						} else if (chart.type == "ordinal") {
							chart.on("click", function(){
								controller.renderAll(panel)
							})
						}
					}
				});

		panel.chart_divs = $(panel.getEl().dom).find('div.freq-chart');
		this.renderAll(panel);
	},

	// Renders the specified chart or list.
	render: function(method) {
		d3.select(this).call(method);
	},

	// Whenever the brush moves, re-rendering everything.
	renderAll: function(panel) {
		for (var i = 0; i < panel.charts.length; i++) {
			panel.charts[i]([panel.chart_divs[i]]);
		}
		panel.charts.forEach(function(chart) {
			if (chart.stacked) {
				chart.transitionStacked();
			} else {
				chart.transitionGrouped();
			}
		})
	}
})
