/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.organizetool.behaviors.Layering', {
     
    alternateClassName: ['Layering'],
     
    statics: {  

          /* 
              function moveToTop(Selection top, String type)
            This function takes a selection and moves all of its elements to the top of 
            a layer (layer "type" to be precise).
          
          */
          
        moveToTop:function(top, layer, svg) {
        
            var onetop = D3Helper.getElFromSel(top);
            
              //all elements on the foreground of the type "type"
            var foreground = svg.selectAll("*[layer=\"" + layer + "\"]");
            
              //zData will contain z indices of the foreground elements. 
            var zData = [];
            foreground.each(function(d) {
                zData.push(parseFloat(this.getAttribute("z")));
            });
                        
              //maxZ: the maximum z-value (the element currently at the top of the layer)
            var maxZ = Math.max.apply(Math, zData);
            var minZ = Math.min.apply(Math, zData);
            
              //how much we need to add. the + 0.5 accounts for half z-index difference between text/expand and container.
              //this half z-index accounts for the fact that text and expand need to always be above the container.
            var diff = maxZ - minZ + 0.5; 
            
              //here we set the z indices (and zData) of top to be one above the current maximum
            top.each(function(d) {
                initZ = parseFloat(this.getAttribute("z"));
                initZIndex = zData.indexOf(initZ);
                zData[initZIndex] += diff;
                
                if (this.getAttribute("use") !== "container") {
                    zData[initZIndex] += 0.5;
                }
                
            })
                .attr("z", function(d) {
                    if (this.getAttribute("use") !== "container"){
                        return parseFloat(this.getAttribute("z")) + diff + 0.5;
                    }
                    else {
                        return parseFloat(this.getAttribute("z")) + diff;
                    }                        
                });
                
              //attatch the data to the foreground selection and sort with the new z values
            foreground
                .data(zData)
                .sort(Layering.compareZ);
                
              //needed in order to get the parent
            var top_container = top.select( function() {
              if(this.getAttribute("use") === "container") {
                  return this;
              }
              else {
                  return null;
              }
              
            });
              
            top_container = D3Helper.getElFromSel(top_container);
            
            var top_children = foreground.select( function (d) {
            
              if(this.getAttribute("parent") === top_container.id && this.getAttribute("type") === "group") {
                  return this;
              }
              else {
                  return null;
              }
              
            });

              //recursion to move top's children to the top of the layer
            if (!top_children.empty()) {
                top_children.each(function(d) {
                    var topChild = svg.selectAll("#" + this.id);
                    Layering.moveToTop(topChild, this.getAttribute("layer"), svg);
                });
            }
        },
        
              //compare function for z axis
        compareZ:function(a, b) {
            if (a > b) {return 1;}
            if (a < b) {return -1;}
            return 0;
        }

    
    }
    
})