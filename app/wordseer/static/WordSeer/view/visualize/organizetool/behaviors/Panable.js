/* Copyright 2012 Aditi Muralidharan. See the file "LICENSE" for the full license governing this code. */Ext.define('WordSeer.view.visualize.organizetool.behaviors.Panable', {

    alternateClassName: ['Panable'],
     
    statics: {     
    
          //this lets you pan by dragging the background
          //a pan is just a drag on objects you are not touching.
        getPanBehavior:function(svg) {

            var pan = d3.behavior.drag()
                .on("dragstart", panstart)
                .on("drag", panmove)
                .on("dragend", panend);

              //if this is the first panmove
            var first = "yes";
            
              //store the previous mouse positions
            var panx = 0;
            var pany = 0;
                
              //called on a mouse down to begin a drag
            function panstart(d, i) {
                 first = "yes";
                 return;
            }
            
              //called when mouse is moved while down
            function panmove(d, i) {
            
                  //previous mouse position
                var befx = panx;
                var befy = pany;
                
                  //current mouse position
                panx = d3.event.x;
                pany = d3.event.y;
                
                  //difference between current and previous mouse position
                var dx = (panx - befx);
                var dy = (pany - befy);
                
                  //don't update on the first panmove
                if( first === "yes") {
                    first = "no";
                    return;
                }
                
                  //update the position, (move the foreground)
                else {  
                    pantick(dx, dy);
                }
            }

              //on a mouse up, but there's nothing to do. 
            function panend(d, i) {

            }
            
              //update the foreground to reflect the pan
            function pantick(dx, dy) { 
            
                  //select and move everything in the foreground
                group = svg.selectAll(".foreground")
                  .attr("transform", function(d) {
                        if (this.getAttribute("transform") !== null) {
                      
                            if(this.tagName === "foreignObject" || this.tagName === "TEXTAREA") {
                                D3Helper.transformXByCoord(this, (dx) );
                                D3Helper.transformYByCoord(this, (dy) );
                                return "";
                            }
                      
                            var initx = D3Helper.getTransformX(this);
                            var inity = D3Helper.getTransformY(this);
                            return "translate(" + (initx + dx) + "," + (inity + dy) + ")";
                        }
                  });
            }    
            
                return pan;
        } 
    
    }
    
})