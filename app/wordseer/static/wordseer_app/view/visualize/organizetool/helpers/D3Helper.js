/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.organizetool.helpers.D3Helper', {

    /*      class D3 Helper
        These are functions written that help deal with some of d3's funky
        framework specificities, and also functions that are convenient based
        on the organize tool's funky specificities.
         
    */
    
    alternateClassName: ['D3Helper'],
     
    statics: { 

          //returns the element from a selection with a single element in it
         getElFromSel:function(selection) {
        
              //the j-index where an element exists
            var j;
            
              //the current j-index in the loop
            var counter = 0;
                                
              //loop until you find an element
            while(selection[0][counter] === null) {
            counter++;
            }
                                
            j = counter;
                    
            return selection[0][j];
        
        },
        
        elCount:function(selection){
        
            var array = selection[0];
            var count = 0;
            var i = 0;
            
            while(i < array.length) {
                if (array[i] !== null) {
                    count++;
                }
                
                i++;
            }
            
            return count;
        
        },

          //a function to get the x coordinate of an element's transform attribute.
          //hard coded.
        getTransformX:function(element) {
            var string = element.getAttribute("transform");
            var index = 10
            var transX = "";
            while (string.charAt(index) != ",") {
                transX = transX + string.charAt(index);
                index++;
            }
            
            return parseInt(transX);
        },
        
          //a function to get the y coordinate of an element's transform attribute.
          //hard coded.
        getTransformY:function(element) {
            var string = element.getAttribute("transform");
            var index = 10
            var transY = "";
            
            while (string.charAt(index) != ",") {
                index++;
            }
            index++;
            
            while (string.charAt(index) != ")") {
                transY = transY + string.charAt(index);
                index++;
            }
            
            return parseInt(transY);
        },

        transformXByCoord:function(element, num) {
            d3.select(element)
                .attr("x", function(d){
                    return (parseInt(this.getAttribute("x")) + num);
                })
        },
        
        transformYByCoord:function(element, num) {
            d3.select(element)
                .attr("y", function(d){
                    return (parseInt(this.getAttribute("y")) + num);
                })
        },
        
          //only use with a string of numbers followed by "px" ex. "300px"
        getIntFromPx:function(string) {
            var i = 0;
            while (i < string.length) {
                if (string.charAt(i) === "p") {
                    break;
                }
                i++;
            }
            
            return parseInt(string.substring(0, i));
        },
        
          //only use with a string of numbers followed by "px" ex. "300px"
        countNL:function(string) {
            var i = 0;
            var count = 0;
            while (i < string.length) {
                if (string.charAt(i) === "\n") {
                    count++;
                }
                i++;
            }
            
            return count;
        },
        
          //function to get the style of an element.
        getStyle:function(oElm, strCssRule){
            var strValue = "";
            
            if(document.defaultView && document.defaultView.getComputedStyle){
                strValue = document.defaultView.getComputedStyle(oElm, "").getPropertyValue(strCssRule);
            }
            
            else if(oElm.currentStyle){
                strCssRule = strCssRule.replace(/\-(\w)/g, function (strMatch, p1){
                    return p1.toUpperCase();
                });
                strValue = oElm.currentStyle[strCssRule];
            }
            
            return strValue;
        },
        
          //a function to get the width of a "type". Different implementations
          //based on the different types. Plan to add code here
        getWidth:function(type, container) {
            switch (type) {           
                case "bubble":
                    return 2 * parseInt(container.getAttribute("r"));
                
                case "group":
                    switch(container.getAttribute("shape")) {
                        case "rectangle":
                            return parseInt(container.getAttribute("width"));
                            break;
                        case "circle":
                            return 2 * parseInt(container.getAttribute("r"));                   
                            break;
                    }
                
                case "annotation":
                    return parseInt(container.getAttribute("width"));
                
                case "document":
                    return parseInt(container.getAttribute("width"));
              
                case "sentence":
                    return parseInt(container.getAttribute("width"));
                    
                case "set":
                    return parseInt(container.getAttribute("width"));
                    
                case "word":
                    return parseInt(container.getAttribute("width"));
            }
            
        },
        
          //a function to get the height of a "type". Different implementations
          //based on the different types. Plan to add code here
        getHeight:function(type, container) {
            switch (type) {
                case "bubble":
                    return 2 * parseInt(container.getAttribute("r"));
                
                case "group":
                    switch(container.getAttribute("shape")) {
                        case "rectangle":
                            return parseInt(container.getAttribute("height"));
                            break;
                        case "circle":
                            return 2 * parseInt(container.getAttribute("r"));                   
                            break;
                    }
                
                case "annotation":
                    return parseInt(container.getAttribute("height"));

                case "document":                   
                    return parseInt(container.getAttribute("height"));
                    
                case "sentence":
                    return parseInt(container.getAttribute("height"));
                    
                case "set":
                    return parseInt(container.getAttribute("height"));

                case "word":
                    return parseInt(container.getAttribute("height"));
            }
        },
        
        fillHover:function(element){
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
                        
            var oldfill = D3Helper.getStyle( D3Helper.getElFromSel(container), "fill");
            container.attr("oldfill",  oldfill);
            var newfill = Color.darken(oldfill);
            
            switch(type){
                case "bubble":
                    container.style("fill", newfill);
                    break;
                    
                case "group":
                    container.style("fill", newfill);
                    break;
                    
                case "annotation":
                    break;
                    
                case "document":
                    container.attr("xlink:href", '../../style/icons/documentHover.png');
                    break;
                    
                case "sentence":
                    container.style("fill", newfill);
                    break;
                    
                case "set":
                    container.style("fill", newfill);
                    break;
 
                case "word":
                    container.style("fill", newfill);
                    break; 
            }

        },
        
        returnHover:function(element){
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
            
            var color = D3Helper.getElFromSel(container).getAttribute("oldfill");
            
            
            
            switch(type){
                case "bubble":      
                    container.style("fill", color);
                    break;
                    
                case "group":
                    container.style("fill", color);
                    break;
                    
                case "annotation":
                    break;
                    
                case "document":
                    container.attr("xlink:href", '../../style/icons/document.png');
                    break;
                    
                case "sentence":
                    container.style("fill", color);
                    break;
                    
                case "set":
                    container.style("fill", color);
                    break;
                    
                case "word":
                    container.style("fill", color);
                    break;
            }

        }

    }
})