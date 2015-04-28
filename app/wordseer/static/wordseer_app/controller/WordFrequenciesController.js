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
		var fstring = momentFormat(prop.date_format);

		// convert dates to desired interval
		var row_headers = prop.sentences[0];
		var rows = _.rest(prop.sentences);

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

		return {rows: rows};
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
				word_frequencies_panel.fireEvent('rendered', word_frequencies_panel);

		    },
		    reset:function(response) {

		    },
		    failure: function(response) {

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
		c3_charts = {};
		var me = this;
		// size params
		var width = 500, height = 350,
			padding = {bottom: 25, right: 20},
			margin = {"top": 0, "bottom": 0, "left": 0, "right": 15};

		var canvas = d3.select(panel.getComponent('canvas').getEl().dom);
		canvas.selectAll('.viz-container').remove();

		// create visibility toggles
		var controls = d3.select('#' + panel.id + ' .panel-header .controls');
		var toggles = controls.selectAll('span')
			.data(_.map(data, function(v,k){
				// d3 wants an array, not an object
				v.property = k;
				return v;
			}))
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
				return d.property;
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
					_.each(c3_charts, function(chart, key){
						if (data[key].datatype == "string" || data[key].datatype == "number") {
							var totals = _.cloneDeep(data[key].totals);
							var remainders = _.cloneDeep(data[key].totals);
							var rows = _.cloneDeep(data[key].sentences);

							_.each(rows, function(row,row_i){
								if (row_i > 0){ // skip the x row
									_.each(_.rest(row), function(col, col_i){
										// skip the label but adjust the index
										var i = col_i + 1;
										remainders[row_i][i] -= col;
									})
								}
							})

							// remainders = _.reject(remainders, function(v){
							// 	return typeof v == 'string'
							// });
							if (remainders.length > 0){
								data[key]['c3_format_norm'] = true
								_.each(remainders, function(v,i){
									if (i == 0) {
										v[1] = "(other)";
									}
									rows[i].push(v[1]);
								})

								// normalize to 100%
								_.each(rows, function(row,row_i){
									if (row_i > 0){
										console.log(row)
										_.each(row, function(c,i,a){
											if (i > 0) {
												console.log(c, totals[row_i])
												a[i] = c / totals[row_i][1];
											}
										})
									}
								})
								chart.load({
									rows: rows
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
					_.each(c3_charts, function(chart, key){
						if (data[key].datatype == "string" || data[key].datatype == "number") {
							var rows = _.clone(data[key].sentences);
							data[key]['c3_format_norm'] = false;
							// unstack the bars
							chart.groups([]);
							// reset axis to max value
							var all_vals = _.flatten(_.rest(rows));
							chart.axis.max({y: _.max(all_vals)});
							chart.load({
								unload: ['(other)'],
								rows: rows
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

		_.each(data, function(val, key){
			var container = canvas.append('div')
				.classed("viz-container", true)
				.classed(makeClassName(key), true) // in util.js
				;

			var viztitle = container.append('div')
				.attr('class', 'property')
				.text(key);

			var download_link = viztitle.append('a')
				.attr('class', 'download')
				.attr('download', function(){
					return "sentence counts across " + key + '.csv';
				});
			// attach to download button as data url
			var file_data = d3.csv.format(val.sentences); // requires d3 >= 3.1
			var data_url = "data:application/octet-stream," +
				escape(file_data);
			download_link.attr("href", data_url);

			download_link.append('i')
				.attr('class', 'fa fa-download');

			var profile = container.append('div')
					.attr("class", "wordfreq")
						;

			// debugger;
			var chart_opts = {
				bindto: profile,
				size: {
					width: width,
					height: height
				},
				padding: padding,
				data: {
					x: 'x',
					rows: val.sentences,
					type: 'bar',
					xSort: true,
					// map query labels to colors
					colors: _.object(_.rest(val.sentences[0]), COLOR_SCALE),
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
								if (data[key].c3_format_norm) {
									return d3.format('.1%')(tick)
								} else {
									if (tick % 1 === 0) {
										return parseInt(tick);
									}
								}
							},
							values: function(range){
								var max = Math.floor(range[1]);
								var values = [];
								var skip = 1;
								if (max > 10) {
									var skip = Math.ceil(max / 10);
								}
								for (var i=0; i<=max; i += skip ) {
									values.push(i);
								}
								return values;
							}
						}
					}
				},
				legend: {
					position: 'bottom',
				}
			};

			if (val.datatype == 'date') {
				var dformat = val.date_format;
				var dformat_moment = momentFormat(dformat); // in util.js

				chart_opts.data.type = 'line';
				chart_opts.axis.x.type = 'timeseries';
				chart_opts.axis.x.tick.fit = false;
				chart_opts.axis.x.tick.rotate = 45;
				chart_opts.axis.x.tick.multiline = false;

				// calculate intervals (requires moment.js)
				// check the range,
				// and also make sure the diffs aren't all exactly the next largest interval
				var dates = _.pluck(_.rest(val.sentences), 0),
					moments = _.map(dates, function(d){
						return moment(d, dformat_moment);
					}),
					dmin = _.min(moments),
					dmax = _.max(moments)
					;

				val.intervals = {
					'year': dmax.diff(dmin, 'years') > 0,
					'month': dmax.diff(dmin, 'months') > 0 && _.some(dates,
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
					'day': dmax.diff(dmin, 'day') > 0 && _.some(dates,
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
					'hour': dmax.diff(dmin, 'hours') > 0 && _.some(dates,
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
					'minute': dmax.diff(dmin, 'minutes') > 0 && _.some(dates,
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
					'second': dmax.diff(dmin, 'seconds') > 0 && _.some(dates,
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

				// TODO: a smarter way to deal with there being only one date value
				if (_.all(val.intervals, function(v){ return v == false; })) {
					val.intervals.day = true;
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
							return val.intervals[k];
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

				var agg = me.aggregateDates(val, selected_date_detail);
				chart_opts.data.rows = agg.rows;
				chart_opts.axis.x.tick.format = function(time){
					var choice = selector
						.select(":checked")
						.property('value')
						;
					return d3.time.format(tickFormats[choice])(time);
				}
			}



			if (val.datatype == "number") {
				chart_opts.axis.x.type = "indexed";
				chart_opts.axis.x.tick.fit = false;
				chart_opts['bar'] = {
					width: {
						ratio: 7 / _.last(_.pluck(val.sentences, 0))
					}
				}
				if (chart_opts.bar.width.ratio > .25) chart_opts.bar.width.ratio = .25;
			}


			var chart = c3.generate(chart_opts);
			// store in global variable to access later
			c3_charts[key] = chart;

			if (val.datatype == "string") {
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
							// retrieve data from chart and configure in rows
							var queries = _.pluck(chart.data(), 'values');
							var x_labels = chart.categories();
							var rows = _.map(x_labels, function(label, i){
								var row = [label];
								_.each(queries, function(q){
									row.push(q[i].value);
								})
								return row;
							});

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

							// add query labels back in after sorting values
							var queries_row = _.map(queries, function(q){
								return q[0].id;
							});
							queries_row.unshift('x');
							rows.unshift(queries_row);

							chart.load({
								rows: rows
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

			if (val.datatype == "date") {
				selector.on('change', function(){
					var choice = d3.select(this)
						.select(":checked")
						.property('value');

					// reload data at new aggregation level
					var new_data = me.aggregateDates(val, choice);
					chart.load(new_data);
				});
			}

		});
	}
});
