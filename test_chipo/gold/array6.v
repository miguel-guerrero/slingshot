// local defines
`define _GET_MSK(w) ((1 << (w)) - 1)
`define _GET_FLD(x, sh, w) (((x) >> (sh)) & `_GET_MSK(w))

//----------------------------------------------------------------------------
// adder
//----------------------------------------------------------------------------
module adder 
#(
    parameter DW = 32,
    parameter NUM_INP = 8)
(
    input [4:0] a,
    input [NUM_INP*DW-1:0] ins,
    output reg [19:0] tbl
);




always @(*) begin : combo_logic
    tbl = `_GET_FLD(ins, a*1*DW, DW)/*[a]*/;
end


endmodule

// local undefines
`undef _GET_MSK
`undef _GET_FLD

