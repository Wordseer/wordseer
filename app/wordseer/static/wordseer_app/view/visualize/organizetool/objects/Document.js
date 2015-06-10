/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.organizetool.objects.Document', {

    alternateClassName: ['Document'],
    
    statics: {         
        id_count: 0,
        
        createDocument:function(dataset, svg, drag, text, count) {
        
            dataset.push( this.id_count );
            
            var x = this.id_count;
            this.id_count++;    
                               
            svg.append("g") 
                .attr("text-align", "center");
                
            var textEl = svg.insert("text", "*[layer=\"0\"]")
                .attr("id", "document" + x + "")
                .attr("class", "foreground")
                .attr("type", "document")
                .attr("use", "text")
                .attr("oldfill", "#000000")
                .attr("layer", 1)
                .attr("z", x + 0.5)
                .attr("x", 0)
                .attr("y", 0)
                .attr("transform", "translate(49,49)")
                .call(function(d){ 
                    MenuOT.giveMenu(this);
                })
                .call(drag); 

            Text.textWrap(text, textEl, 20); 
            Text.tspanCenter(textEl);            
                            
            var safebox = svg.selectAll("rect[type=\"document\"]")
                .data(dataset)
                .enter().insert("rect", "#document" + x + "")
                .style("stroke", "black")
                .style("stroke-width", 1)
                .style("fill", "#F9F7F7")
                .style("opacity", 0)
                .attr("id", "document" + x + "")
                .attr("class", "foreground")
                .attr("type", "document")
                .attr("use", "none")
                .attr("layer", 1)
                .attr("parent", "none")
                .attr("z", x)
                .attr("x", -8)
                .attr("y", -4.5)
                .attr("dx", 7)
                .attr("dy", 7)
                .attr("width", function(d) {
                    var bbox = D3Helper.getElFromSel(textEl).getBBox();
                    return bbox.width + 16;
                })
                .attr("height", function(d) {
                    var bbox = D3Helper.getElFromSel(textEl).getBBox();
                    return bbox.height + 16;
                })
                .attr("transform", "translate(49,49)")
                .call(drag);
                            
            var document = svg.insert("image", "*[layer=\"0\"]")
                .attr("id", "document" + x + "")
                .attr("class", "foreground")
                .attr("type", "document")
                .attr("use", "container")
                .attr("layer", 1)
                .attr("parent", "none")
                .attr("xlink:href", '../../style/icons/document.png')
                .attr("z", x)
                .attr("x", 0)
                .attr("y", 0)
                .attr("width", 50)
                .attr("height", 50)
                .attr("transform", function(d) {
                    var bbox = D3Helper.getElFromSel(textEl).getBBox();
                    
                    return "translate(" + ( 49 + (bbox.width / 2)  - 25) + "," + (49 + bbox.height) + ")";
                })
                .call(function(d){ 
                    MenuOT.giveMenu(this);
                })
                .call(drag);
                             

                             
            var newDoc = svg.selectAll("#document" + x + "")
                .transition()
                .duration(150)
                .attr("transform", function(d) {
                    var window = D3Helper.getElFromSel(svg).parentNode;
                    var height = D3Helper.getStyle(window, "height");
                    height = D3Helper.getIntFromPx(height);
                    return "translate(" + ( D3Helper.getTransformX(this) + (count * 120) ) + "," + (height - 150 + D3Helper.getTransformY(this) ) + ")";
                }); 
                         
            return document;  
        },

        removeDocument:function(el, dataset, svg) {
            var x = dataset[dataset.length - 1];
            
            svg.selectAll("#" + el.id)
                .remove();
            
            dataset.pop();
        },
    
    },
    
}) 