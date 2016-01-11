/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.organizetool.behaviors.Dragable', {

    alternateClassName: ['Dragable'],
     
    statics: {     
           //the behavior to drag an element.       
        getDragBehavior:function(svg){
            var drag_behavior = d3.behavior.drag()
                .on("dragstart", dragstart)
                .on("drag", dragmove)
                .on("dragend", dragend);


                
              //if this is the first movement, we don't want to call dragtick.
              //we just want to get the initial dragx and dragy positions 
              //(dx and dy will not work right on fencepost case)
            var dragfirst = "yes";
            
              //the position of the mouse
            var dragx = 0;
            var dragy = 0;
            
              //for dragmove
            var timeout;
            var hovering = false;
            
              //this occurs when you click to start a drag
            function dragstart(d, i) {
            
                 dragfirst = "yes";
                   
                   //we want whatever we are draggging to be on the top of its layer
                 var top = svg.selectAll("#" + this.id);
                 Layering.moveToTop(top, this.getAttribute("layer"), svg);
                 
                 return;
            }


              //this occurs when the mouse is held down for a drag
            function dragmove(d, i) {
                  
                hovering = false;
                D3Helper.returnHover(this);
                var me = this;
                  
                if (timeout !== null) {
                    clearTimeout(timeout);
                }
                
                var group = this.id;
                var type = this.getAttribute("type");
                
                timeout = setTimeout(function() { 
                    D3Helper.fillHover(me);
                    hovering = true;
                    
                }, 500);
                
                  //befx and befy are the coordinates of the previous mouse position used to find dx and dy
                var befx = dragx;
                var befy = dragy;
                
                dragx = d3.event.x;
                dragy = d3.event.y;
                
                  //dx and dy: how far x and y have changed; how much to update this' position
                var dx = (dragx - befx);
                var dy = (dragy - befy);
             
                  //if dragfirst, then don't update.
                if( dragfirst === "yes") {
                    dragfirst = "no";
                    return;
                }
                
                  //otherwise call dragtick to handle the update.
                else {
                    
                    dragtick(dx, dy, group, type);
                }
            }

              //this happens when you lift the mouse up to finish a drag.
            function dragend(d, i) {
            
                    clearTimeout(timeout);
                    
                    D3Helper.returnHover(this);
            
                    var group = this.id;
                    
                      //get the current values of x and y, this is not necessary later, it is used for the trash can
                    var x = D3Helper.getTransformX(this);
                    var y = D3Helper.getTransformY(this);
                    
                      //handle any collisions with objects in the foreground
                    CollisionHandling.handleCollisions(this, svg, hovering);
                    
            }
            
              //essentially an update method for dragmove
            function dragtick(dx, dy, group, type) { 
            
                  //drag the whole id-group
                var toDrag = svg.selectAll("#" + group + "")
                  .attr("transform", function(d) {
               
                        if(this.tagName === "foreignObject" || this.tagName === "TEXTAREA") {
                            D3Helper.transformXByCoord(this, (dx) );
                            D3Helper.transformYByCoord(this, (dy) );
                            return "";
                        }

                      var initx = D3Helper.getTransformX(this);
                      var inity = D3Helper.getTransformY(this);                         
                      
                      return "translate(" + (dx + initx) + "," + (dy + inity)+ ")";          
                  });
                  
                  //you must drag this element's children

                   var container = toDrag.select(function(d) {
                       if(this.getAttribute("use") === "container") { return this; }
                       else { return null; }
                    });
                    
                container = D3Helper.getElFromSel(container); 
                
                GroupHierarchy.moveAllChildren(container, dx, dy, svg);
                  
                
            }
         
            return drag_behavior;
         
        }

    }

})