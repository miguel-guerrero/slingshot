// local defines
`define _GET_MSK(w) ((1 << (w)) - 1)
`define _GET_FLD(x, sh, w) (((x) >> (sh)) & `_GET_MSK(w))

//----------------------------------------------------------------------------
// adder
//----------------------------------------------------------------------------
module adder (
    input [4:0] a,
    input [639:0] ins,
    output reg [19:0] tbl
);




always @(*) begin : combo_logic
    tbl = `_GET_FLD(ins, a*1*20, 20)/*[a]*/;
end


endmodule

// local undefines
`undef _GET_MSK
`undef _GET_FLD

