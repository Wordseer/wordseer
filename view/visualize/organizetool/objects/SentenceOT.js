/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.organizetool.objects.SentenceOT', {

      //sentence (organize tool)
    alternateClassName: ['SentenceOT'],
    
    statics: {
        id_count: 0,
        
        createSentence:function(dataset, svg, drag, text) {
        
            dataset.push( this.id_count );
            
            var x = this.id_count++; //get sentence number and increase ID count
            svg.append("g") 
                .attr("text-align", "end");
            var textEl = svg.insert("text", "*[layer=\"0\"]")
                .attr("id", "sentence" + x + "")
                .attr("class", "foreground")
                .attr("type", "sentence")
                .attr("use", "text")
                .attr("layer", 1)
                .attr("z", x + 0.5)
                .attr("x", 0)
                .attr("y", 0)
                .attr("font-weight", "bold")
                .attr("transform", "translate(49,49)")
                .call(function(d){ 
                    MenuOT.giveMenu(this);
                })
                .call(drag);
                
            Text.textWrap(text, textEl, 50);

            var sentence = svg.insert("rect", "#sentence" + x + "")
                .style("stroke", "#777")
                .style("stroke-width", 1)
                .style("fill", "#F9F7F7")
                .style("opacity", "0.8")
                .attr("oldfill", "F9F7F7")
                .attr("id", "sentence" + x + "")
                .attr("class", "foreground")
                .attr("type", "sentence")
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
                
            var newSent = svg.selectAll("#sentence" + x + "").transition()
                .duration(150)
                .attr("transform", function(d) {
                    var window = D3Helper.getElFromSel(svg).parentNode;
                    var height = D3Helper.getStyle(window, "height");
                    height = D3Helper.getIntFromPx(height);
                    return "translate(" + 10 + "," + (height - (parseInt(D3Helper.getElFromSel(sentence).getAttribute("height")) + 15) ) + ")";
                }); 
                
            var ot = OrganizeTool.getInstance();
            ot.updateShape(1, "rounded");               
            
            return sentence;
        },

        removeSentence:function(el, dataset, svg) {
            var x = dataset[dataset.length - 1];
            
            svg.selectAll("#" + el.id)
                .remove();
            
            dataset.pop();
        },
    
    },
    
}) 
