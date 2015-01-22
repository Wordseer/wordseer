/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.organizetool.objects.Annotation', {

    alternateClassName: ['Annotation'],
     
    statics: {     
    
        id_count: 1,
    
        createAnnotation:function(dataset, svg, drag, text) {
                
            dataset.push( this.id_count );
            
            var x = this.id_count;
            this.id_count++; 
        
            if ( text === undefined) {
                text = "new annotation " + x + "";
            }
        
            var annotation = svg.append("rect")
                .style("fill", "#CCCCCC")
                .style("stroke", "black")
                .style("stroke-width", "1")
                .style("opacity", "0.99")
                .attr("id", "annotation" + x + "")
                .attr("class", "foreground")
                .attr("type", "annotation")
                .attr("layer", 0)
                .attr("use", "container")
                .attr("oldfill", "#FFEE99")
                .attr("parent", "none")
                .attr("transform", "translate(0,0)")
                .attr("xlink:href", '../../style/icons/annotation.png')
                .attr("x", 0)
                .attr("y", 0)
                .attr("z", x)
                .attr("width", 159)
                .attr("height", 15)
                .call(drag)
                .call(function(d){ 
                    MenuOT.giveMenu(this);
                });
                
            var shortened = svg.append("text")
                .attr("id", "annotation" + x + "")
                .attr("class", "foreground")
                .attr("type", "annotation")
                .attr("layer", 0)
                .attr("use", "shortenedtxt")
                .attr("parent", "none")
                .attr("transform", "translate(0,0)")
                .attr("x", 2)
                .attr("y", 12)
                .attr("z", (x + 0.2) )
                .text("")
                .call(drag);   
                
            var annotation = svg.append("rect")
                .style("fill", "#DFDFDF")
                .style("stroke", "black")
                .style("stroke-width", "1")
                .style("opacity", "0.99")
                .attr("id", "annotation" + x + "")
                .attr("class", "foreground")
                .attr("type", "annotation")
                .attr("layer", 0)
                .attr("use", "minimize")
                .attr("parent", "none")
                .attr("transform", "translate(0,0)")
                .attr("x", 145)
                .attr("y", 2)
                .attr("z", x + 0.1)
                .attr("rx", 3)
                .attr("ry", 3)
                .attr("width", 11)
                .attr("height", 11)
                .on("mousedown", function(d) {
                    Annotation.minimize(this, svg);
                });

            svg.append("text")
                .attr("id", "annotation" + x + "")
                .attr("class", "foreground")
                .attr("type", "annotation")
                .attr("layer", 0)
                .attr("use", "mintxt")
                .attr("parent", "none")
                .attr("transform", "translate(0,0)")
                .attr("x", 148)
                .attr("y", 11)
                .attr("z", (x + 0.2) )
                .text("-")
                .on("mousedown", function(d) {
                    Annotation.minimize(this, svg);
                });                

                
            var annotationtxt = svg.append("foreignObject");
                
            annotationtxt
                .attr("id", "annotation" + x + "")
                .attr("class", "foreground")
                .attr("type", "annotation")
                .attr("layer", 0)
                .attr("use", "fo")
                .attr("parent", "none")
                .attr("z", x)
                .attr("x", 0)
                .attr("y", 15)
                .attr("width", 160)
                .attr("height", 175)
                .attr("transform", "translate(0,0)")
                .call(function(d){ 
                    MenuOT.giveMenu(this);
                })
                    .append("xhtml:form")
                    .append("textarea")
                        .text(text)
                        .style("height", 17)
                        .style("width", 160)
                        .style("background-color", "#FFEE99")
                        .style("resize", "none")
                        .attr("use", "text")
                        .attr("id", "annotation" + x + "")
                        .attr("z", x)
                        .on("keyup", function(d) {
                           var text = this.value
                           this.innerHTML = text; 
                           
                           var tspan = svg.append("text")
                               .text(text)
                               .attr("id", "randomIDfortest");
                               
                            var width = D3Helper.getElFromSel(tspan).getBBox().width;
                            
                            d3.select("#randomIDfortest").remove();
                            
                            var nl_count = D3Helper.countNL(text);
                                                        
                            var newHeight = parseInt(width / 146);
                            
                            var change = newHeight + nl_count;
                            
                            if( change > 10) {
                                change = 10;
                            }
                            
                            d3.select(this)
                                .style("height", (17 + ((change) * 15) ))
                                .attr("oldtxt", text);
                            
                            var foo = d3.selectAll("#" + this.id).select(function(d){
                                if(this.getAttribute("use") === "fo") {
                                    return this;
                                }
                                    
                                else {
                                    return null;
                                }
                            });
                            
                        });    
                /*
            var safebox = svg.selectAll("rect[type=\"annotation\"]")
                .data(dataset)
                .enter().insert("rect", "#annotation" + x + "")
                .style("stroke", "black")
                .style("stroke-width", 1)
                .style("fill", "#F9F7F7")
                .style("opacity", 0)
                .attr("id", "annotation" + x + "")
                .attr("class", "foreground")
                .attr("type", "annotation")
                .attr("use", "none")
                .attr("layer", 1)
                .attr("parent", "none")
                .attr("z", x)
                .attr("x", -8)
                .attr("y", 11.5)
                .attr("dx", 7)
                .attr("dy", 7)
                .attr("width", function(d) {
                    var bbox = D3Helper.getElFromSel(annotationtxt).getBBox();
                    return bbox.width + 16;
                })
                .attr("height", function(d) {
                    var bbox = D3Helper.getElFromSel(annotationtxt).getBBox();
                    return bbox.height + 16;
                })
                .attr("transform", "translate(0,0)")
                .call(drag);
                */
                
            var newAn = svg.selectAll("#annotation" + x + "").transition()
                .duration(150)
                .attr("transform", function(d) {
                    var window = D3Helper.getElFromSel(svg).parentNode;
                    var height = D3Helper.getStyle(window, "height");
                    height = D3Helper.getIntFromPx(height);
                                        
                    if(this.tagName === "foreignObject" || this.tagName === "TEXTAREA") {
                        D3Helper.transformXByCoord(this, 10);
                        D3Helper.transformYByCoord(this, height - 70);
                        return "";
                    }
                    
                    return "translate(" + 10 + "," + (height - 70) + ")";
                });   
                
            return annotation;
                
        },
        
        removeAnnotation:function(el, dataset, svg) {
            var x = dataset[dataset.length - 1];
            
            svg.selectAll("#" + el.id)
                .remove();
            
            dataset.pop();
        },
        
        minimize:function(element) {
            var svg = OrganizeTool.getInstance().canvas
            var textarea = svg.selectAll("#" + element.id).select(function(d) {
                if(this.getAttribute("use") === "fo") {
                    return this;
                }
                
                else {
                   return null;
                }
            });
            
            textarea
                .attr("height", 0)
                .style("opacity", 0);
                           
            
            d3.select(element).on("mousedown", function(d) {
                Annotation.maximize(this, svg);
            });
            
            var shortenedtxt = d3.selectAll("#" + element.id).select(function(d) {
                if(this.getAttribute("use") === "shortenedtxt") {
                    return this;
                }
                
                else {
                   return null;
                }            
            });
            
            if(textarea.text().length < 22) {
                shortenedtxt.text(textarea.text());
            }
            
            else {
                shortenedtxt.text(textarea.text().substring(0, 21) + "...");
            }
            
            var textarea = svg.selectAll("#" + element.id).select(function(d) {
                if(this.getAttribute("use") === "mintxt") {
                    return this;
                }
                
                else {
                   return null;
                }
            })
                .text("+")
                .attr("x", 146)
                .on("mousedown", function(d) {
                Annotation.maximize(this, svg);
            });

        },
        
        maximize:function(element, svg) {
            var textarea = svg.selectAll("#" + element.id).select(function(d) {
                if(this.getAttribute("use") === "fo") {
                    return this;
                }
                
                else {
                   return null;
                }
            });
            
            textarea
                .attr("height", 175)
                .style("opacity", 1);
            
            d3.select(element).on("mousedown", function(d) {
                Annotation.minimize(this, svg);
            });
            
            var textarea = svg.selectAll("#" + element.id).select(function(d) {
                if(this.getAttribute("use") === "mintxt") {
                    return this;
                }
                
                else {
                   return null;
                }
            })
                .text("-")
                .attr("x", 148)
                .on("mousedown", function(d) {
                Annotation.minimize(this, svg);
            });
            
            var shortenedtxt = d3.selectAll("#" + element.id).select(function(d) {
                if(this.getAttribute("use") === "shortenedtxt") {
                    return this;
                }
                
                else {
                   return null;
                }            
            });
            
            shortenedtxt.text("");
            
        }
    
    }
    
})