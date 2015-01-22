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
	aggregateDates: function(prop, selected_date_detail){
		// retrieve format string from type
		var fstring = momentFormat(prop.type.slice(5));

		// convert dates to desired interval
		var row_headers = _.zip(prop.columns)[0];
		var rows = _.rest(_.zip(prop.columns));

		var new_rows = d3.nest()
			.key(function(d){
				return moment(d[0], fstring)
					.startOf(selected_date_detail)
					.valueOf();
			})
			.sortKeys(d3.ascending)
			.rollup(function(leaves){
				var totals = []
				for (var i = 1; i < leaves[0].length; i++) {
					totals.push(d3.sum(leaves, function(d){
						return d[i];
					}));
				}
				return totals
			})
			.entries(rows)
			;

		rows = _.map(new_rows, function(row){
			return _.flatten([parseInt(row.key), row.values])
		});

		rows.unshift(row_headers);
		var new_columns = _.zip(rows)

		return {columns: new_columns};
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

				// ***********************
				// wordfreq reiplementation code here
				// ***********************
				// // reconfigure data for nv.d3
				// var resp = Ext.decode(response.responseText),
				// data = [],
				// sentences = resp.counts[0].sentences,
				// prop_names = [];
				//
				// d3.keys(sentences[0]).forEach(function(k){
				// 	if (k.indexOf('__') >= 0) {
				// 		var components = k.split('__');
				// 		var type = components[0],
				// 		name = components[1];
				// 		prop_names.push(name);
				// 		var prop = {
				// 			'property': name,
				// 			'type': type,
				// 			'streams': [{
				// 				'key': resp.counts[0].query.gov,
				// 				'values': [],
				// 			}],
				// 		};
				// 		var unique = {};
				// 		sentences.forEach(function (sent) {
				// 			if (!unique[sent[k]] && typeof sent[k] !== 'undefined') {
				// 				prop.streams[0].values.push({
				// 					"x": isNaN(Number(sent[k]))? sent[k] : Number(sent[k]),
				// 					"y": sentences.filter(function(s){
				// 						return s[k] == sent[k];
				// 					}).length,
				// 				});
				// 				unique[sent[k]] = true;
				// 			}
				// 		});
				// 		// sort by the x value (categorical)
				// 		prop.streams[0].values.sort(function(a,b){
				// 			return a.x < b.x ? -1 : a.x > b.x ? 1 : 0;
				// 		})
				// 		data.push(prop);
				// 	}
				// });
				//
				// word_frequencies_panel.data = data;
				//
				//
				// // new or update
				// if (word_frequencies_panel.down('#canvas').el.dom.childElementCount == 1){
				// 	this.draw(data, word_frequencies_panel);
				// } else {
				// 	this.updateCharts(data);
				// }
				//
				// word_frequencies_panel.fireEvent('rendered', word_frequencies_panel);

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

	/** Draws a WordFrequencies.
	@param {Object} data The data structure containing a list of lists, where
	each list contains sentence records, each with complete metadata, that match
	each search in the {@link WordSeer.model.FormValues#search} values.
	frequencies.
	@param {WordSeer.view.visualize.wordfrequencies.WordFrequencies} panel the
	view in which the wordfrequencies is currently being drawn.
	*/
	draw: function(data, panel){
		c3_charts = [];
		var me = this;
		// size params
		var width = 500, height = 350,
			padding = {bottom: 25, right: 20},
			margin = {"top": 0, "bottom": 0, "left": 0, "right": 15};

		var canvas = d3.select(panel.getComponent('canvas').getEl().dom);

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
				// reset all the sort controls
				d3.selectAll('.sort-control')
					.attr('class', 'sort-control fa fa-sort-alpha-asc')
					.selectAll('.sort-menu i')
						.classed('selected', function(d){
							return d == 'fa-sort-alpha-asc';
						});

				if (d.value == "norm") {
					// normalize data to total for profile
					_.each(c3_charts, function(chart, index){
						if (data[index].type == "string" || data[index].type == "number") {
							var totals = _.cloneDeep(data[index].total_counts);
							var remainders = _.cloneDeep(data[index].total_counts);
							var cols = _.cloneDeep(data[index].columns);

							_.each(cols[0], function(key,i){
								if (i > 0){
									_.each(_.rest(cols), function(c){
										remainders[key] -= c[i]
									})
								}
							})

							remainders = _.reject(remainders, function(v){
								return typeof v == 'string'
							});
							if (remainders.length > 0){
								data[index]['c3_format_norm'] = true
								var other = _.toArray(remainders);
								other.unshift("(other)");
								cols.push(other);

								// normalize to 100%
								_.each(cols[0], function(key,i){
									if (i > 0){
										_.each(_.rest(cols), function(c){
											c[i] = c[i] / totals[key];
										})
									}
								})
								chart.load({
									columns: cols
								});

								// formatting changes
								chart.data.colors({'(other)': '#d4d4d4'})
								var groups = _.pluck(chart.data(), 'id');
								groups.push("(other)");
								chart.groups([groups]);
								chart.axis.max({y: 0.99})
							}
						}
					})
				} else if (d.value == "raw"){
					// de-normalize the data
					_.each(c3_charts, function(chart, index){
						if (data[index].type == "string" || data[index].type == "number") {
							var cols = _.clone(data[index].columns);
							data[index]['c3_format_norm'] = false;
							// unstack the bars
							chart.groups([]);
							// reset axis to max value
							var all_vals = _.flatten(_.rest(cols));
							chart.axis.max({y: _.max(all_vals)});
							chart.load({
								unload: ['(other)'],
								columns: cols
							})
						}
					})
				}
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

		data.forEach(function(prop, index){
			var container = canvas.append('div')
				.classed("viz-container", true)
				.classed(makeClassName(prop.property), true) // in util.js
				;

			var viztitle = container.append('div')
				.attr('class', 'property')
				.text(prop.displayName);

			var download_link = viztitle.append('a')
				.attr('class', 'download')
				.attr('download', function(){
					return "sentence counts across " + prop.displayName + '.csv';
				});

			download_link.append('i')
				.attr('class', 'fa fa-download');

			var profile = container.append('div')
					.attr("class", "wordfreq")
						;

			var chart_opts = {
				bindto: profile,
				size: {
					width: width,
					height: height
				},
				padding: padding,
				data: {
					x: 'x',
					columns: prop.columns,
					type: 'bar',
					xSort: true,
					colors: prop.color,
				},
				axis: {
					x: {
						type: 'category',
						tick: {
							culling: {
								max: 9
							},
							fit: true,
							multiline: true,
							width: 45,
						},
					},
					y: {
						label: '# of sentences',
						tick: {
							format: function(tick) {
								if (data[index].c3_format_norm) {
									return d3.format('.1%')(tick)
								} else {
									return parseInt(tick);
								}
							}
						}
					}
				},
				legend: {
					position: 'bottom',
				}
			};

			if (prop.type.search(/^date_/) >= 0) {
				var dformat = prop.type.slice(5);
				var dformat_moment = momentFormat(dformat); // in util.js

				chart_opts.data.type = 'line';
				chart_opts.axis.x.type = 'timeseries';
				chart_opts.axis.x.tick.fit = false;
				chart_opts.axis.x.tick.rotate = 45;
				chart_opts.axis.x.tick.multiline = false;

				// calculate intervals (requires moment.js)
				// check the range,
				// and also make sure the diffs aren't all exactly the next largest interval
				var dmin = moment(prop.columns[0][1], dformat_moment),
					dmax = moment(_.last(prop.columns[0]), dformat_moment)
					;

				prop.intervals = {
					'year': dmax.diff(dmin, 'years') > 0,
					'month': dmax.diff(dmin, 'months') > 0 && _.some(_.rest(prop.columns[0]),
						function(v,i,a){
							if (a[i+1] != undefined){
								var current = moment(v, dformat_moment),
									next = moment(a[i+1], dformat_moment)
									;
								return current.diff(next, 'years', true) != current.diff(next, 'years');
							} else {
								return false;
							}
						}
					),
					'day': dmax.diff(dmin, 'day') > 0 && _.some(_.rest(prop.columns[0]),
						function(v,i,a){
							if (a[i+1] != undefined){
								var current = moment(v, dformat_moment),
								next = moment(a[i+1], dformat_moment)
								;
								return current.diff(next, 'months', true) != current.diff(next, 'months');
							} else {
								return false;
							}
						}
					),
					'hour': dmax.diff(dmin, 'hours') > 0 && _.some(_.rest(prop.columns[0]),
						function(v,i,a){
							if (a[i+1] != undefined){
								var current = moment(v, dformat_moment),
								next = moment(a[i+1], dformat_moment)
								;
								return current.diff(next, 'days', true) != current.diff(next, 'days');
							} else {
								return false;
							}
						}
					),
					'minute': dmax.diff(dmin, 'minutes') > 0 && _.some(_.rest(prop.columns[0]),
						function(v,i,a){
							if (a[i+1] != undefined){
								var current = moment(v, dformat_moment),
								next = moment(a[i+1], dformat_moment)
								;
								return current.diff(next, 'hours', true) != current.diff(next, 'hours');
							} else {
								return false;
							}
						}
					),
					'second': dmax.diff(dmin, 'seconds') > 0 && _.some(_.rest(prop.columns[0]),
						function(v,i,a){
							if (a[i+1] != undefined){
								var current = moment(v, dformat_moment),
								next = moment(a[i+1], dformat_moment)
								;
								return current.diff(next, 'minutes', true) != current.diff(next, 'minutes');
							} else {
								return false;
							}
						}
					)
				}

				var tickFormats = {
					'second': "%x %X",
					'minute': '%x %H:%M',
					'hour': '%x %H:00',
					'day': '%x',
					'month': '%m/%Y',
					'year': '%Y',
				};

				// add dropdown selector for date granularity
				var selector = container.append('div')
					.attr('class', 'timeselect')
					.append('select')
					;

				container.select('.timeselect')
					.insert('span', ':first-child')
					.text('detail level: ')

				var intervals_order = ['year', 'month', 'day', 'hour', 'minute', 'second'];

				selector.selectAll('option')
					.data(_.filter(intervals_order, function(k){
							return prop.intervals[k];
						})
					)
					.enter()
					.append('option')
					.attr('value', function(d){ return d; })
					.text(function(d){ return d; })
					.property('checked', function(d,i){ return i == 0; })
					;

				// aggregate dates into the largest meaningful interval
				var selected_date_detail = selector.selectAll(':checked')
					.property('value');

				var agg = me.aggregateDates(prop, selected_date_detail);
				chart_opts.data.columns = agg.columns;
				chart_opts.axis.x.tick['format'] = tickFormats[selected_date_detail];
			}



			if (prop.type == "number") {
				chart_opts.axis.x.type = "indexed";
				chart_opts.axis.x.tick.fit = false;
				chart_opts['bar'] = {
					width: {
						ratio: 7 / _.last(prop.columns[0])
					}
				}
			}


			var chart = c3.generate(chart_opts);
			// store in global variable to access later
			c3_charts.push(chart);

			if (prop.type == "string") {
				// add a sort control
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
						.on('click', function(d){
							// TODO: use chart.data, it's live
							var cols_obj = _.pluck(chart.data(), 'values');
							var cols = _.map(cols_obj, function(col){
								return _.pluck(col, 'value');
							})
							var x_col = chart.categories();
							cols.unshift(x_col);
							var rows = _.zip(cols);
							switch(d){
								case 'fa-sort-alpha-asc':
									rows = _.sortBy(rows, 0);
									break;
								case 'fa-sort-alpha-desc':
									rows = _.sortBy(rows, 0).reverse();
									break;
								case 'fa-sort-amount-asc':
									rows = _.sortBy(rows, 1);
									break;
								case 'fa-sort-amount-desc':
									rows = _.sortBy(rows, 1).reverse();
									break;
							}
							// append header on rows
							var row_labels = _.pluck(chart.data(), 'id');
							row_labels.unshift("x");
							rows.unshift(row_labels);
							// unzip the rows back into columns and reload
							chart.load({
								columns: _.zip(rows)
							})

							// update menu display and current sort icon
							d3.select(this.parentElement)
								.selectAll('i')
								.classed('selected', false)
								;

							d3.select(this)
								.classed('selected', true)
								;

							sort_control.attr('class', 'sort-control fa ' + d);

						})
						;

			}

			/*

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

				if (prop.type.search(/^date_/) >= 0){
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
				if (prop.type == "string" || prop.type == "number") {
					var keys = chart.xAxis.domain();
					for (var i = 0; i < keys.length; i++){
						var row = {};
						row[prop.property] = keys[i];
						// add each stream freq
						prop.streams.forEach(function(stream){
							var matching_value = stream.values.filter(function(v){
								return v.x == keys[i];
							});
							row[stream.key] = matching_value[0].y;
						});

						data_export.push(row);
					}
				} else if (prop.type.search(/^date_/) >= 0) {
					// make a set of all date values from all streams
					var all_dates = d3.set();
					prop.streams.forEach(function(stream){
						stream.values_orig.forEach(function(v){
							all_dates.add(v.x);
						});
					});

					// find matching values for each stream, or 0 if none
					all_dates.forEach(function(this_date){
						var row = {};
						row[prop.property] = this_date;
						// add each stream freq
						prop.streams.forEach(function(stream){
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
*/
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
			// var datum = data[i];

			// Deep copy so we don't overwrite original data objects
			var datum = $.extend(true, {}, data[i]);

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

	}

});
