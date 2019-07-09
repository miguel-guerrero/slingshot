//----------------------------------------------------------------------------
// cater
//----------------------------------------------------------------------------
module cater 
#(
    parameter WIDTH = 8)
(
    input [WIDTH-1:0] x,
    input [WIDTH-1:0] y,
    output reg [3:0] cat,
    input clk,
    input rst_n,
    input a,
    input b
);




always @(*) begin : combo_logic
    cat <= {x[3:2], y[2]};
    cat <= (a ^ b) & cat ^ a;
end


endmodule


