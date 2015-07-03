require("../env");

var vows = require("vows"),
    assert = require("assert");

var suite = vows.describe("d3.svg.brush");

suite.addBatch({
  "brush": {
    topic: function() {
      return d3.svg.brush;
    },

    "x": {
      "defaults to null": function(brush) {
        assert.isNull(brush().x());
      }
    },

    "y": {
      "defaults to null": function(brush) {
        assert.isNull(brush().y());
      }
    },

    "extent": {
      "returns null when no scales are attached": function(brush) {
        assert.isNull(brush().extent());
      },
      "returns a one-dimensional array if only x is defined": function(brush) {
        var b = brush().x(d3.scale.linear());
        assert.deepEqual(b.extent(), [0, 0]);
      },
      "takes a one-dimensional array if only x is defined": function(brush) {
        var b = brush().x(d3.scale.linear()).extent([0.1, 0.4]);
        assert.deepEqual(b.extent(), [0.1, 0.4]);
      },
      "returns a one-dimensional array if only y is defined": function(brush) {
        var b = brush().y(d3.scale.linear());
        assert.deepEqual(b.extent(), [0, 0]);
      },
      "takes a one-dimensional array if only y is defined": function(brush) {
        var b = brush().y(d3.scale.linear()).extent([0.1, 0.4]);
        assert.deepEqual(b.extent(), [0.1, 0.4]);
      },
      "returns a two-dimensional array if x and y are defined": function(brush) {
        var b = brush().x(d3.scale.linear()).y(d3.scale.linear());
        assert.deepEqual(b.extent(), [[0, 0], [0, 0]]);
      },
      "takes a two-dimensional array if x and y are defined": function(brush) {
        var b = brush().x(d3.scale.linear()).y(d3.scale.linear()).extent([[0.1, 0.2], [0.3, 0.4]]);
        assert.deepEqual(b.extent(), [[0.1, 0.2], [0.3, 0.4]]);
      },
      "preserves the set extent exactly": function(brush) {
        var lo = new Number(0.1),
            hi = new Number(0.3),
            b = brush().x(d3.scale.linear()).extent([lo, hi]),
            extent = b.extent();
        assert.strictEqual(extent[0], lo);
        assert.strictEqual(extent[1], hi);
      }
    }
  }
});

suite.export(module);
