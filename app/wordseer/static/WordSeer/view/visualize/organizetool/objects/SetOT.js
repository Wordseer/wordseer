/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.organizetool.objects.SetOT', {

      //sentence (organize tool)
    alternateClassName: ['SetOT'],
    
    statics: {         
        id_count: 0,
        
        createSet:function(dataset, svg, drag, text) {
        
            dataset.push( this.id_count );
            
            var x = this.id_count;
            this.id_count++;    
                
            svg.append("g") 
                .attr("text-align", "end");
                
            var textEl = svg.insert("text", "*[layer=\"0\"]")
                .attr("font-weight", "bold")
                .attr("id", "set" + x + "")
                .attr("class", "foreground")
                .attr("type", "set")
                .attr("use", "text")
                .attr("layer", 1)
                .attr("z", x + 0.5)
                .attr("x", 0)
                .attr("y", 0)
                .attr("transform", "translate(49,49)")
                .call(function(d){ 
                    MenuOT.giveMenu(this);
                })
                .call(drag);  
                
            Text.textWrap(text, textEl, 50);

               
            var set = svg.insert("rect", "#set" + x + "")
                .style("stroke", "#777")
                .style("stroke-width", 1)
                .style("fill", "#F9F7F7")
                .style("opacity", "0.8")
                .attr("oldfill", "F9F7F7")
                .attr("id", "set" + x + "")
                .attr("class", "foreground")
                .attr("type", "set")
                .attr("use", "container")
                .attr("shape", "rounded")
                .attr("layer", 1)
                .attr("parent", "none")
                .attr("z", x)
                .attr("x", -8)
                .attr("y", -4.5)
                .attr("rx", 15)
                .attr("ry", 15)
                .attr("width", function(d) {
                    var bbox = D3Helper.getElFromSel(textEl).getBBox();
                    return bbox.width + 16;
                })
                .attr("height", function(d) {
                    var bbox = D3Helper.getElFromSel(textEl).getBBox();
                    return bbox.height + 16;
                })
                .attr("transform", "translate(49,49)")
                .call(function(d){ 
                    MenuOT.giveMenu(this);
                })
                .call(drag); 
                
            var newSet = svg.selectAll("#set" + x + "").transition()
                .duration(150)
                .attr("transform", function(d) {
                    var window = D3Helper.getElFromSel(svg).parentNode;
                    var height = D3Helper.getStyle(window, "height");
                    height = D3Helper.getIntFromPx(height);
                    return "translate(" + 10 + "," + (height - (parseInt(D3Helper.getElFromSel(set).getAttribute("height")) + 15) ) + ")";
                }); 
                
            var ot = OrganizeTool.getInstance();
            ot.updateShape(1, "rounded");            
            
            return set;
            
        },

        removeSet:function(el, dataset, svg) {
            var x = dataset[dataset.length - 1];
            
            svg.selectAll("#" + el.id)
                .remove();
            
            dataset.pop();
        },
    
    },
    
}) 