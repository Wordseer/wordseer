/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.organizetool.Color', {

    
    alternateClassName: ['Color'],
     
    statics: { 

        changeColor:function(element, color){
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
            
            var text = svg.selectAll("#" + element.id).select(function() {
                if(this.getAttribute("use") === "text") {
                    return this;
                }
                
                else {
                    return null;
                }
            });
            
            ot.updateColor(-1, D3Helper.getElFromSel(container).getAttribute("oldfill"));
            
            switch(type){
                case "bubble":      
                    container.style("fill", color).attr("oldfill", color);
                    break;
                    
                case "group":
                    container.style("fill", color).attr("oldfill", color);
                    break;
                    
                case "annotation":
                    
                    var textarea = svg.selectAll("#" + element.id).select(function() {
                        if(this.getAttribute("use") === "text") {
                            return this;
                        }
                        
                        else {
                            return null;
                        }
                    });
                    
                    textarea.style("background-color", color);
                    container.attr("oldfill", color);
                    
                    var fo = svg.selectAll("#" + element.id).select(function() {
                        if(this.getAttribute("use") === "fo") {
                            return this;
                        }
                        
                        else {
                            return null;
                        }
                    });
                                                
                    break;
                    
                case "document":
                    text.style("fill", Color.darken(Color.darken(Color.darken(color)))).attr("oldfill", color);
                    break;
                    
                case "sentence":
                    container.style("fill", color).attr("oldfill", color);;
                    break;
                    
                case "set":
                    container.style("fill", color).attr("oldfill", color);;
                    break;
                    
                case "word":
                    container.style("fill", color).attr("oldfill", color);;
                    break;
            }
            
            ot.updateColor(1, color);

        },
        
        changeGroupColor:function(element, color){
            var ot = OrganizeTool.getInstance();
            var canvas = ot.canvas;
            
//            console.log(element.id);
            
            var children = canvas.selectAll(".foreground").select(function(d) {
                if(GroupHierarchy.isDescendant(this, element, canvas) ) {
//                    console.log("child: " + this.id);
                    return this;
                }
                else {
                    return null;
                }
            });
            
//            console.log(children);
            
            children.each(function(d) {
                Color.changeColor(this, color);
            });

            Color.changeColor(element, color);
        },
  
        darken:function(color){
            var rStr = color.substring(1,3);
            var gStr = color.substring(3,5);
            var bStr = color.substring(5,7);
            
            var darkR = parseInt(rStr, 16) - 32;
            var darkG = parseInt(gStr, 16) - 32;
            var darkB = parseInt(bStr, 16) - 32;
            
            if (darkR < 0) {
                darkR = "00";
            }
 
            if (darkG < 0) {
                darkG = "00";
            }
            
            if (darkB < 0) {
                darkB = "00";
            }            
            var darkColor = "#" + darkR.toString(16) + darkG.toString(16) + darkB.toString(16);
            return darkColor;
        }

    }
})