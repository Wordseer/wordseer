/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.barchart.BarCharts',{
    extend:'Ext.panel.Panel',
    requires:[
        'WordSeer.view.visualize.barchart.BarChart',
    ],
    alias:'widget.bar-charts',
    title:'Word Frequencies',
    height: 250,
    autoScroll: true,
    layout: {
        type: 'hbox',
        align: 'stretchmax',
    },
    initComponent:function(){
        this.callParent(arguments);
        this.launcher = Ext.create('WordSeer.view.desktop.BarChartModule', {});
        this.govChart = Ext.widget('bar-chart',{
            flex:1
        });
        this.depChart = Ext.widget('bar-chart', {
            flex:1
        });
        this.govChart.otherChart = this.depChart;
        this.govChart.filtered = false;
        this.govChart.formValues = {};
        this.govChart.parentPanel = this;
        this.depChart.otherChart = this.govChart;
        this.depChart.filtered = false;
        this.depChart.formValues = {};
        this.depChart.parentPanel = this;
        this.add(this.govChart);
        this.add(this.depChart);
    },
    listeners:{
        search:function(formValues){
            this.formValues = formValues;
            if(formValues.search.length > 0){
                Ext.apply(this, formValues);
                Ext.apply(this, formValues.search[0]);
                var params = Ext.apply({
                    statistics:'true',
                    user:getUsername(),
                    instance:getInstance(),
                }, formValues.serialize());
                Ext.apply(params, formValues.search[0]);
                this.data = Ext.Ajax.request({
                    url:'../../src/php/grammaticalsearch/get-search-results.php',
                    method:'GET',
                    params:params,
                    timeout: 9000000,
                    scope:this,
                    success:this.updateCharts
                })
            }
        },
        chartsFiltered:function(){
            var dep = this.depChart.clickValues.join(" ")
            var deptype = 'word';
            var gov = this.govChart.clickValues.join(" ")
            var govtype = 'word';
            if(dep.length == 0){
                dep = this.dep
                deptype = this.deptype;
            }
            if(gov.length == 0){
                gov = this.gov
                govtype = this.govtype;
            }
            filteredFormValues = Ext.apply({}, this.formValues);
            filteredFormValues.search[0].dep = dep;
            filteredFormValues.search[0].gov = gov;
            filteredFormValues.search[0].govtype = govtype
            filteredFormValues.search[0].deptype = deptype;
            Ext.apply(filteredFormValues, filteredFormValues.search[0]);
            var me = this;
            this.up('widget').items.each(function(){
                if(this.xtype != me.xtype){
                    this.fireEvent('search', filteredFormValues, this);
                }
            })
            // this.up('widget').dockedItems.each(function(){
            //     if(this.itemId == "browse"){
            //         this.fireEvent('search', filteredFormValues, this);
            //     }
            // })
        }
    },
    updateCharts:function(response){
        this.data = Ext.decode(response.responseText)['statistics'];
        if(this.relation != 2){
            this.updateChart(this.govChart, this.data.gov.children, this.data.gov.childMax, 'gov');
            this.updateChart(this.depChart, this.data.dep.children, this.data.dep.childMax, 'dep');
        }
        else if (this.relation == 1){
            //"any relation" query
            // -- merge graphs, merge-sort data
            var queryWords = getWords()
            var d = [];
            var gov = this.data.gov.children;
            var dep = this.data.dep.children;
            var max = 0;
            var finished = false;
            var gov_i = 0, dep_i = 0;
            while(!finished){
                var currentGov = gov[gov_i];
                var currentDep = dep[dep_i];
                var govValue =currentGov.value;
                currentGov.category = 'gov';
                var depValue = currentDep.value;
                currentDep.category = 'dep';
                if(max < govValue){
                    max = govValue
                }
                if(max < depValue){
                    max = depValue
                }
                if(depValue > govValue){
                    d.push(currentGov);
                    gov_i++;
                }else{
                    d.push(currentDep);
                    dep_i++
                }
                finished = (gov_i >= gov.length || dep_i >= dep.length);
            }
            if(gov_i < gov.length){
                while(gov_i < gov.length){
                    var currentGov = gov[gov_i];
                    currentGov.category = 'gov';
                    if(max < currentGov.value){
                        max = currentGov.value
                    }
                    d.push(currentGov);
                    gov_i++;
                }
            }
            if(dep_i < dep.length){
                while(dep_i < dep.length){
                    var currentDep = dep[dep_i];
                    currentDep.category = 'dep';
                    if(max < currentDep.value){
                        max = currentDep.value
                    }
                    d.push(currentDep);
                    dep_i++;
                }
            }
            this.updateChart(this.govChart, d, max);
            this.updateChart(this.depChart, [], max);
        }else{// a search query //TODO look into this, it has problems
            console.dir(); //TODO delete
            this.updateChart(this.govChart, [], 0, 'gov');
            this.updateChart(this.depChart, [], 0, 'dep');
        }
        this.doLayout();
    },
    updateChart:function(chart, data, maxValue, category){
        if(data.length > 0){
            var d = [];
            for(var i = 0; i < data.length; i++){
                var type = ('category' in data[i])? data[i].category : category;
                d.push({'name':data[i].name, 'value':data[i].value, 'children':data[i].children, 'category':type, 'childMax':data[i].childMax})
            }
            chart.data = d;
            chart.max = maxValue;
            Ext.defer(function(d, maxValue){// Give the chart area 1 second  to open.
                chart.drawData(d, maxValue);
                this.show();
            }, 1000, this, [d, maxValue, true]);
        } else {
            chart.hide();
            if(this.govChart.isHidden() && this.depChart.isHidden()){
                this.hide();
            }else{
                this.show();
            }
        }

    }
})
