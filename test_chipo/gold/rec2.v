//----------------------------------------------------------------------------
// adder
//----------------------------------------------------------------------------
module adder 
#(
    parameter W = 8)
(
    input clk,
    input [4*W:0] ins,
    input rst_n,
    output reg [W+1:0] sm,
    output reg [W+1:0] sm_r,
    output reg sm_zero_r
);




always @(*) begin : combo_logic
    sm = ins/*.s.x*/[W-1:0] + ins/*.s.y*/[2*W-1:W] + ins/*.s.z*/[3*W-1:2*W] + ins/*.s.w*/[4*W-1:3*W] + ins/*.cin*/[4*W];
end


always @(posedge clk or negedge rst_n) begin : registering
    if (~rst_n) begin
        sm_r <= 0;
        sm_zero_r <= 0;
    end
    else begin
        sm_r <= sm;
        sm_zero_r <= sm == 0;
    end
end


endmodule


