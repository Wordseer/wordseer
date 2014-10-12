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
					sentences = resp.counts[0].sentences,
					prop_names = [];

				d3.keys(sentences[0]).forEach(function(k){
					if (k.indexOf('__') >= 0) {
						var components = k.split('__');
						var type = components[0],
							name = components[1];
						prop_names.push(name);
						var prop = {
							'property': name,
							'type': type,
							'streams': [{
								'key': resp.counts[0].query.gov,
								'values': [],
							}],
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
		// size params
		var width = 380, height = 300,
			padding = {"top": 5, "bottom": 5, "left": 5, "right": 5},
			margin = {"top": 0, "bottom": 0, "left": 0, "right": 15};

		var canvas = d3.select(panel.getComponent('canvas').getEl().dom);
		var chart;

		data.forEach(function(x){
			var container = canvas.append('div')
				.attr("class", "viz-container");

			container.append('div')
				.attr('class', 'property')
				.text(x.property);

			var svg = container.append('div')
					.attr("class", "wordfreq")
						.append('svg')
						.attr("class", x.property)
						.datum(x.streams);

			var chart;
			nv.addGraph(function() {
			    if (x.type == "string" || x.type == "number") {
					chart = nv.models.multiBarChart()
					.transitionDuration(300)
					.delay(0)
					.groupSpacing(0.45)
					.staggerLabels(false)
					.defaultState({"stacked": true})
					.showLegend(false)
					.showControls(false)
					.showXAxis(true)
					.reduceXTicks(true)
					.color(function(){ return COLOR_SCALE[0]})
					;

					chart.multibar
					.hideable(false);

					if (x.streams[0].values.length < 25) {
						chart.reduceXTicks(false);
					}

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

					var format = d3.time.format(format_string);
					x.streams.forEach(function(stream){
						// copy original for user transformations later
						if (!('values_orig' in stream)) {
							stream.values_orig = $.extend(true, [], stream.values);
						}
						var newvalues = [];
						d3.nest()
							.key(function(v){
								var date = format.parse(String(v.x));
								// TODO: let user choose granularity level
								v.x = d3.time[selected_date_detail](date);
								return v.x;
							})
							.sortKeys(function(a,b){
								var aa = new Date(a),
									bb = new Date(b);
								return aa - bb;
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

					chart = nv.models.lineChart()
						.transitionDuration(350)
						.showLegend(false)
						.showYAxis(true)
						.useInteractiveGuideline(true)
						.color(function(){ return COLOR_SCALE[0]})
						.showXAxis(true)
						.xScale(d3.time.scale())
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
					.axisLabel('Number of Sentences')
					.axisLabelDistance(40);

				chart.xAxis
					// .staggerLabels(true)
					.showMaxMin(true)
					.rotateLabels(45)
					;

				chart.margin({left: 55, bottom: 100, right: 45});
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
					// fire change event for timeseries granularity
					selector.on('change', function(){
						var choice = d3.select(this)
							.select(":checked")
							.property('value');
						panel.fireEvent('changeDateDetail', chart,
										choice, date_detail, format);

					});
				}
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
				.sortKeys(d3.ascending)
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
	}

});
