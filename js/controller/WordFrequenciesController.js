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
				'changeDateDetail': this.changeDateDetail,
			},
		});
	},

	/** Helper function to decode datetime format string returned by server
	**/
	formatDateTime: function(x, selected_date_detail){
		// retrieve format string from type
		var format_string = x.type.slice(5);

		var format = d3.time.format(format_string);
		x.streams.forEach(function(stream){
			// sort values first
			stream.values.sort(function(a,b){
				var aa = format.parse(String(a.x)),
					bb = format.parse(String(b.x));
				return aa - bb;
			})

			// copy original for user transformations later
			if (!('values_orig' in stream)) {
				stream.values_orig = $.extend(true, [], stream.values);
			}
			var newvalues = [];
			d3.nest()
				.key(function(v){
					var date = format.parse(String(v.x));
					v.x = d3.time[selected_date_detail](date);
					return v.x;
				})
				.rollup(function(leaves){
					var point = {
						'x': leaves[0].x,
						'y': d3.sum(leaves, function(d){
								return d.y;
							})
					};
					newvalues.push(point);
					return point;
				})
				.entries(stream.values)
				;
			stream.values = newvalues;
		})
		;
		return format;
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
		var values = formValues.serialize();
		Ext.Ajax.request({
		    url:'../../src/php/word-frequencies/bar-charts.php',
		    method:'GET',
		    disableCaching: false,
		    timeout: 900000,
		    params: Ext.apply({
		        metadata:formValues.metadata,
		        phrases: formValues.phrases,
		        user:getUsername(),
		        instance:getInstance(),
		    }, values),
		    scope:this,
		    success:function(response){
		        // reconfigure data for nv.d3
				var resp = Ext.decode(response.responseText),
		        	data = [],
					sentences = resp.counts[0].sentences;

				d3.keys(sentences[0]).forEach(function(k){
					if (k.indexOf('__') >= 0) {
						var components = k.split('__');
						var type = components[0],
							name = components[1];
						if (resp.for_normalization[name] != undefined) {
							var display_name = resp.for_normalization[name]
								.displayName;
							var total_counts = {};
							resp.for_normalization[name].children.forEach(function(d){
								total_counts[d.text] = d.count;
							})
						} else {
							var display_name = name,
								total_counts = {};

						}

						var prop = {
							'property': name,
							'displayName': display_name,
							'type': type,
							'streams': [{
								'key': resp.counts[0].query.gov,
								'values': [],
							}],
							'total_counts': total_counts,
						};

						var unique = {};
						sentences.forEach(function (sent) {
						  if (!unique[sent[k]] && typeof sent[k] !== 'undefined') {
						    prop.streams[0].values.push({
								"x": isNaN(Number(sent[k]))? sent[k] : Number(sent[k]),
								"y": sentences.filter(function(s){
										return s[k] == sent[k];
									}).length,
								});
							unique[sent[k]] = true;
						  }
						});
						// sort by the x value (categorical)
						prop.streams[0].values.sort(function(a,b){
							return a.x < b.x ? -1 : a.x > b.x ? 1 : 0;
						})
						data.push(prop);
					}
				});

				word_frequencies_panel.data = data;


				// new or update
				if (word_frequencies_panel.down('#canvas').el.dom.childElementCount == 0){
					this.draw(data, word_frequencies_panel);
				} else {
					this.updateCharts(data, word_frequencies_panel.id);
				}

				word_frequencies_panel.fireEvent('rendered', word_frequencies_panel);
		    },
		    reset:function(response) {

		    },
		    failure: function(response) {
				// debugger;
				var canvas = word_frequencies_panel.down('#canvas');
				canvas.getEl()
					.createChild({
						tag: 'h3',
						html: "request to server failed. please try again or try another query."
					});
				word_frequencies_panel.fireEvent('rendered', word_frequencies_panel);
		    }
		})
	},

	/** Draws a WordFrequencies.
	@param {Object} data The data structure containing a list of lists, where
	each list contains sentence records, each with complete metadata, that match
	each search in the {@link WordSeer.model.FormValues#search} values.
	frequencies.
	@param {WordSeer.view.visualize.wordfrequencies.WordFrequencies} panel the
	view in which the wordfrequencies is currently being drawn.
	*/
	draw: function(data, panel){
		var me = this;
		// size params
		var width = 380, height = 300,
			padding = {"top": 5, "bottom": 5, "left": 5, "right": 5},
			margin = {"top": 0, "bottom": 0, "left": 0, "right": 15};

		var canvas = d3.select(panel.getComponent('canvas').getEl().dom);
		var chart;

		// create visibility toggles
		var controls = d3.select('#' + panel.id + ' .panel-header .controls');
		var toggles = controls.selectAll('span')
			.data(data)
			.enter()
				.append('span')
				.attr('class', 'viz-toggle')
				;
		toggles.append('input')
			.attr('type', 'checkbox')
			.property('checked', 'checked')
			.attr('id', function(d){
				return makeClassName(d.property)+'check'; // in util.js
			})
			.property('value', function(d){
				return makeClassName(d.property); // in util.js
			})
			.on('change', function(d){
				var check = this;
				var target = canvas.select('.viz-container.' + check.value);
				if (check.checked){
					target.transition()
						.style('margin-left', 0)
							.transition()
							.style('opacity', 1)
							;
				} else {
					target.transition()
						.style('opacity', 0)
							.transition()
							.style('margin-left', -9999)
							;
				}
			})
			;

		toggles.append('label')
			.text(function(d){
				return d.displayName;
			})
			.attr('for', function(d){
				return makeClassName(d.property)+'check'; // in util.js
			})
			;

		// create normalize toggle
		var display = d3.select('#' + panel.id + ' .panel-header .display');
		var norm = display.selectAll('span')
			.data([{'value': 'raw', 'label': 'Raw Counts'},
				   {'value': 'norm', 'label': '% of Total'}
			])
			.enter()
				.append('span')
				.attr('class', 'viz-toggle')
				;
		norm.append('input')
			.attr('type', 'radio')
			.attr('value', function(d){
				return d.value;
			})
			.attr('name', 'display_' + panel.id)
			.attr('id', function(d){
				return d.value + '_' + panel.id;
			})
			.property('checked', function(d){
				return d.value == 'raw';
			})
			.on('change', function(d,i){
				var total = data[i].total_count;
				var svg = d3.selectAll('#'+panel.id+' .viz-container svg');
				if (d.value == "norm") {
					// normalize data to total for profile
					svg
						.datum(function(datum,index){
							if (data[index].type == "string" || data[index].type == "number") {
								totals = d3.map(data[index].total_counts);
								remainders = d3.map(data[index].total_counts);

								datum.forEach(function(query){
									query.values.forEach(function(v,i,a){
										// console.log(v.x, v.y)
										if (totals.has(v.x)){
											var rem = remainders.get(v.x);
											remainders.set(v.x, rem - v.y);
										}
									});
								});

								if (remainders.size() > 0){
									// debugger;
									remainders.forEach(function(k,v){
										if (typeof v == 'string'){
											remainders.remove(k);
										}
									});

									var other_values = [];
									remainders.forEach(function(k,v){
										other_values.push({'x': k, 'y': v});
									});
									var other = {
										'key': '(other)',
										'values': other_values
									};
									datum.push(other);

									datum.forEach(function(row){
										row.values = row.values.map(function(v){
											return {
												x: v.x,
												y: v.y / parseInt(totals.get(v.x))
											};
										})
									})
								}
							}
							// TODO: we don't really have the proper data returned to
							// normalize reliably at all intervals for dates
							return datum;
						})
						;
					nv.graphs.forEach(function(g){
						var has_other = g.container.__data__.some(function(v){
							return v.key == "(other)" && v.values != [];
						});
						if (has_other) {
							g.stacked(true);
							var pct_format = d3.format(".0%");
							g.yAxis.tickFormat(function(d){
								return pct_format(d);
							});
						}

					});

				} else if (d.value == "raw") {
					// restore original data
					svg.datum(function(datum,index){
						if (datum.some(function(v){
							return v.key == '(other)';
						})){
							datum = datum.filter(function(v){
								return v.key != "(other)";
							});

							totals = d3.map(data[index].total_counts);

							datum.forEach(function(row){
								row.values = row.values.map(function(v){
									return {
										x: v.x,
										y: v.y * parseInt(totals.get(v.x))
									};
								})
							})
						}



						return datum;
					});

					nv.graphs.forEach(function(g){
						g.yAxis.tickFormat(function(d){
							return d;
						})
					})
				}

				me.updateCharts();
			})
			;
		norm.append('label')
			.attr('for', function(d){
				return d.value + '_' + panel.id;
			})
			.text(function(d){
				return d.label;
			})
			;

		data.forEach(function(x){
			var container = canvas.append('div')
				.classed("viz-container", true)
				.classed(makeClassName(x.property), true) // in util.js
				;

			var viztitle = container.append('div')
				.attr('class', 'property')
				.text(x.displayName);

			var download_link = viztitle.append('a')
				.attr('class', 'download')
				.attr('download', function(){
					return "sentence counts across " + x.displayName + '.csv';
				});

			download_link.append('i')
				.attr('class', 'fa fa-download');

			var svg = container.append('div')
					.attr("class", "wordfreq")
						.append('svg')
						.attr("class", "nvd3")
						.datum(x.streams);

			var chart;
			nv.addGraph(function() {
			    if (x.type == "string" || x.type == "number") {
					chart = nv.models.multiBarChart()
						.delay(0)
						.groupSpacing(0.45)
						.staggerLabels(false)
						.showLegend(false)
						.showControls(false)
						.showXAxis(true)
						.reduceXTicks(false)
						.color(function(d,i){
							if (d.key == "(other)") {
								return '#a1a1a1'
							}
							return COLOR_SCALE[i];
							})
						;

					chart.xAxis
						.scale(d3.scale.ordinal());

					// add a sorting control to the viz title
					var sort_control = viztitle.append('span')
						.attr('class', 'sort')
							.append('i')
							.attr('class', 'sort-control fa fa-sort-alpha-asc')
							;

					// default sorting
					sort_control
						// add a menu to change sorting
						.append('div')
						.attr('class', 'sort-menu')
						.selectAll('i')
							.data([
								'fa-sort-alpha-asc',
								'fa-sort-alpha-desc',
								'fa-sort-amount-asc',
								'fa-sort-amount-desc'
							])
							.enter()
							.append('i')
							.attr('class', function(d, i){
								var classval = 'fa ' + d;
								if (i == 0) { classval += ' selected'; }
								return classval;
							})
							.on('click', function(d, i){
								svg.datum(function(data){
									switch (i) {
										case 0:
											// alpha asc
											data[0].values.sort(function(a,b){
												return d3.ascending(a.x, b.x);
												});
											break;
										case 1:
											// alpha desc
											data[0].values.sort(function(a,b){
												return d3.descending(a.x, b.x);
												});
											break;
										case 2:
											// value asc
											data[0].values.sort(function(a,b){
												return d3.ascending(a.y, b.y);
												});
											break;
										case 3:
											// value desc
											data[0].values.sort(function(a,b){
												return d3.descending(a.y, b.y);
												});
											break;
										default:
											// don't do nothin
											break;
									}
									return data;
								});

								// update menu display and current sort icon
								d3.select(this.parentElement)
									.selectAll('i')
									.classed('selected', false)
									;

								d3.select(this)
									.classed('selected', true)
									;

								sort_control.attr('class', 'sort-control fa ' + d);
								chart.update();

							})
							;



				} else if (x.type.search(/^date_/) >= 0) {
					// retrieve format string from type
					var format_string = x.type.slice(5);

					// determine date granularity options
					date_detail = d3.map();
					// start with compound string format codes
					if (format_string.indexOf('%c') >= 0) {
						date_detail.set('second', "%x %X");
						date_detail.set('minute', '%x %H:%M');
						date_detail.set('hour', '%x %H:00');
						date_detail.set('day', '%x')
						date_detail.set('month', '%m/%Y')
						date_detail.set('year', '%Y')
					} else {
						// piece by piece
						// time
						if (format_string.indexOf('%X') >= 0 ||
								format_string.indexOf('%S') >= 0) {
							date_detail.set('second', "%x %X");
							date_detail.set('minute', '%x %H:%M');
							date_detail.set('hour', '%x %H:00');
						} else if (format_string.indexOf('%M') >= 0){
							date_detail.set('minute', '%x %H:%M');
							date_detail.set('hour', '%x %H:00');
						} else if (format_string.indexOf('%H') >= 0 ||
									format_string.indexOf('%I') >= 0) {
							date_detail.set('hour', '%x %H:00');
						}
						// date
						if (format_string.indexOf('%x') >= 0 ||
								format_string.indexOf('%j') >= 0 ||
								format_string.indexOf('%d') >= 0 ||
								format_string.indexOf('%e') >= 0) {
							date_detail.set('day', '%x')
							date_detail.set('month', '%m/%Y')
							date_detail.set('year', '%Y')
						} else if (format_string.indexOf('%m') >= 0 ||
									format_string.indexOf('%b') >= 0 ||
									format_string.indexOf('%B') >= 0) {
							date_detail.set('month', '%m/%Y')
							date_detail.set('year', '%Y')
						} else if (format_string.indexOf('%y') >= 0 ||
									format_string.indexOf('%Y') >= 0) {
							date_detail.set('year', '%Y')
						}
					}

					// add dropdown selector for date granularity
					var selector = container.append('div')
						.attr('class', 'timeselect')
						.append('select')
							;

					container.select('.timeselect')
						.insert('span', ':first-child')
						.text('detail level: ')

					selector.selectAll('option')
						.data(date_detail.keys()).enter()
						.append('option')
						.attr('value', function(d){ return d; })
						.text(function(d){ return d; });

					// default selection
					if (date_detail.has('day')) {
						selector.select('option[value=day]')
							.property('selected', 'selected')
					} else if (date_detail.has('month')) {
						selector.select('option[value=month]')
							.property('selected', 'selected')
					} else if (date_detail.has('year')) {
						selector.select('option[value=year]')
							.property('selected', 'selected')
					}

					var selected_date_detail = selector.select(':checked')
						.property('value');

					var format = me.formatDateTime(x, selected_date_detail);

					chart = nv.models.lineChart()
						.showLegend(false)
						.showYAxis(true)
						.color(COLOR_SCALE[0])
						.showXAxis(true)
						.xScale(d3.time.scale())
						.forceY(0)
						;

					chart
						.xAxis
							.tickFormat(function(v){
								var format = d3.time.format(
										date_detail.get(selected_date_detail)
										)
								return format(d3.time.scale().invert(v));
								})
						;
				}
				chart.yAxis
			        // .ticks
					.tickFormat(d3.format(',d'))
					.highlightZero(true)
					.axisLabel('Sentence count')
					.rotateYLabel(false)
					;

				chart.xAxis
					.rotateLabels(45)
					.tickValues(function(d){
						var ticks = [];
						if (d[0].values.length < 20) {
							d[0].values.forEach(function(v){
								ticks.push(v.x);
							})
						} else {
							var interval = Math.ceil(d[0].values.length / 20);
							d[0].values.forEach(function(v,i){
								if (i % interval == 0) {
									ticks.push(v.x);
								} else {
									ticks.push('');
								}
							})
						}
						return ticks;
					})
					;

				chart.margin({left: 55, bottom: 100, right: 45});
				chart.transitionDuration(500);
				chart.tooltipContent(function(key, x, y, e, graph){
					return '<table class="nv-pointer-events-none">' +
						'<tr class="nv-pointer-events-none">'+
							'<td class="key nv-pointer-events-none">' +
							x +
							'</td>'+
							'<td class="value nv-pointer-events-none">' +
							y +
							'</td>'+
						'</tr>'+
					'</table>';
				});

				svg.call(chart);


				// fade out overflowing labels
				svg.append("linearGradient")
			      .attr("id", "fadeToWhiteY")
				  .attr("x1", 0).attr("y1", 0)
			      .attr("x2", 0).attr("y2", 1)
			    .selectAll("stop")
			      .data([
			        {offset: "0%", opacity: "0"},
			        {offset: "100%", opacity: "1"}
			      ])
			    .enter().append("stop")
			      .attr("offset", function(d) { return d.offset; })
			      .attr("stop-color", "#FFFFFF")
				  .attr("stop-opacity", function(d){ return d.opacity; })
				;
				svg.append("linearGradient")
				.attr("id", "fadeToWhiteX")
				.attr("x1", 0).attr("y1", 0)
				.attr("x2", 1).attr("y2", 0)
				.selectAll("stop")
				.data([
					{offset: "0%", opacity: "0"},
					{offset: "100%", opacity: "1"}
				])
				.enter().append("stop")
				.attr("offset", function(d) { return d.offset; })
				.attr("stop-color", "#FFFFFF")
				.attr("stop-opacity", function(d){ return d.opacity; })
				;

				var fadesize = 15;
				// bottom edge
				svg.append('rect')
					.attr('width', '100%')
					.attr('height', fadesize)
					.attr('x', 0)
					.attr('y', function(){
						return this.parentElement.offsetHeight - fadesize;
					})
					.attr('fill', 'url(#fadeToWhiteY)');
				// right edge
				svg.append('rect')
					.attr('height', '100%')
					.attr('width', fadesize)
					.attr('x', function(){
						return this.parentElement.offsetWidth - fadesize;
					})
					.attr('y', 0)
					.attr('fill', 'url(#fadeToWhiteX)');

				nv.utils.windowResize(chart.update);

				if (x.type.search(/^date_/) >= 0){
					// fire change event for timdebugger;eseries granularity
					selector.on('change', function(){
						var choice = d3.select(this)
							.select(":checked")
							.property('value');
						panel.fireEvent('changeDateDetail', chart,
										choice, date_detail, format);

					});
				}

				// Make the export data.
				var data_export = [];

				// need to handle dates differently than other datatypes
				if (x.type == "string" || x.type == "number") {
					var keys = chart.xAxis.domain();
					for (var i = 0; i < keys.length; i++){
						var row = {};
						row[x.property] = keys[i];
						// add each stream freq
						x.streams.forEach(function(stream){
							var matching_value = stream.values.filter(function(v){
								return v.x == keys[i];
							});
							row[stream.key] = matching_value[0].y;
						});

						data_export.push(row);
					}
				} else if (x.type.search(/^date_/) >= 0) {
					// make a set of all date values from all streams
					var all_dates = d3.set();
					x.streams.forEach(function(stream){
						stream.values_orig.forEach(function(v){
							all_dates.add(v.x);
						});
					});

					// find matching values for each stream, or 0 if none
					all_dates.forEach(function(this_date){
						var row = {};
						row[x.property] = this_date;
						// add each stream freq
						x.streams.forEach(function(stream){
							var matching_value = stream.values_orig.filter(function(v){
								return v.x == this_date;
							});
							if (matching_value.length) {
								row[stream.key] = matching_value[0].y;
							} else {
								row[stream.key] = 0;
							}
						});
						data_export.push(row);
					});

				}

				// attach to download button as data url
				file_data = d3.csv.format(data_export); // requires d3 >= 3.1
				var data_url = "data:application/octet-stream," +
					escape(file_data);
				download_link.attr("href", data_url);

			    return chart;
			});

		});
	},

	changeDateDetail: function(chart, choice, date_detail, format) {
		var data = d3.select(chart.container).datum();
		data.forEach(function(stream){
			var newvalues = [];
			d3.nest()
				.key(function(d){
					var date = format.parse(String(d.x));
					return d3.time[choice](date);
				})
				.rollup(function(leaves){
					var date = format.parse(String(leaves[0].x));
					var point = {
						'x': d3.time[choice](date),
						'y': d3.sum(leaves, function(d){
								return d.y;
							})
					};
					newvalues.push(point);
					return point;
				})
				.entries(stream.values_orig)
				;

			stream.values = newvalues;
		})
		;
		// bind new data
		d3.select(chart.container).datum(data);
		// update x axis ticks
		chart.xAxis
			.tickFormat(function(v){
				var format = d3.time.format(
					date_detail.get(choice)
				);
				return format(d3.time.scale().invert(v));
			})
		;
		chart.update();
	},

	updateCharts: function(data, panel_id){
		var me = this;
		var svg = d3.selectAll('#' + panel_id + ' .viz-container svg');
		svg.datum(function(d,i){
			datum = data[i];
			if (datum.type.search(/^date_/) >= 0){
				var selected_date_detail = d3.select(this.offsetParent)
					.select('.timeselect')
						.select(':checked')
						.property('value');

				me.formatDateTime(datum, selected_date_detail);
			}
			return datum.streams;
		})
		nv.graphs.forEach(function(g){
			g.update();
		})

	},

});
