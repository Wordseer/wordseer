/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.organizetool.ShapeOT', {
    
    alternateClassName: ['ShapeOT'],
     
    statics: { 

        changeShape:function(element, shape){
            var type = element.getAttribute("type");         
            var ot = OrganizeTool.getInstance();
            var svg = ot.canvas;
            
            var container = svg.selectAll("#" + element.id).select(function() {
                if(this.getAttribute("use") === "container") {
                    return this;
                }
                
                else {
                    return null;
                }
            });
            
            ot.updateShape(-1, D3Helper.getElFromSel(container).getAttribute("shape"));
            
            switch(type){                   
                case "sentence":
                    if(shape === "rounded") {
                        container
                            .attr("rx", 15)
                            .attr("rx", 15)
                            .attr("shape", shape);
                    } 
                    
                    if(shape === "right") {
                        container
                            .attr("rx", 0)
                            .attr("rx", 0)
                            .attr("shape", shape);
                    }
                    
                    break;
                    
                case "set":
                    if(shape === "rounded") {
                        container
                            .attr("rx", 15)
                            .attr("rx", 15)
                            .attr("shape", shape);
                    } 
                    
                    if(shape === "right") {
                        container
                            .attr("rx", 0)
                            .attr("rx", 0)
                            .attr("shape", shape);
                    }
                    
                    break;
                    
                case "word":
                    if(shape === "rounded") {
                        container
                            .attr("rx", 15)
                            .attr("rx", 15)
                            .attr("shape", shape);
                    } 
                    
                    if(shape === "right") {
                        container
                            .attr("rx", 0)
                            .attr("rx", 0)
                            .attr("shape", shape);
                    }
                    
                    break;
            }
            
            ot.updateShape(1, shape);

        },

        changeAllGroupShape:function(element, shape){
            var ot = OrganizeTool.getInstance();
            var canvas = ot.canvas;
            
            var children = canvas.selectAll(".foreground").select(function(d) {
                if(GroupHierarchy.isDescendant(this, element, canvas) ) {
                    return this;
                }
                else {
                    return null;
                }
            });
            
            children.each(function(d) {
                ShapeOT.changeShape(this, shape);
            });

        },
        
        changeShapeOfGroup:function(el, shape) {
            var ot = OrganizeTool.getInstance();
            var svg = ot.canvas;

            switch(shape) {
                case 1:
                    roundness = 0;
                    break;
                    
                case 2:
                    roundness = 30;
                    break;
                    
                case 3:
                    roundness = 80;
                    break; 
                   
            }
            
            var container = svg.selectAll("#" +el.id + "").select(function(d) {
                if(this.getAttribute("use") === "container") {
                    return this;
                }
                else {
                    return null;
                }
            });
                    
            var containerEl = D3Helper.getElFromSel(container);
                    
            ot.updateShape(-1, containerEl.getAttribute("shape"));
                    
            container
                .attr("rx", roundness)
                .attr("ry", roundness)
                .attr("shape", function(d){
                    if(roundness === 0) {
                        return "right";
                    }
                            
                    else {
                        return "rounded";
                    }
                });
                      
            ot.updateShape(1, containerEl.getAttribute("shape"));
        },        

        
    }
})