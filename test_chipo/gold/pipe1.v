//----------------------------------------------------------------------------
// pipe
//----------------------------------------------------------------------------
module pipe 
#(
    parameter W = 8)
(
    input clk,
    input [W-1:0] x,
    input [W-1:0] y,
    output reg [2*W+1:0] arith_s2,
    output reg [2*W-1:0] out
);

reg [W:0] arith_stg1_s;
reg [W-1:0] arith_stg1_x;
reg [2*W+1:0] arith_stg2_s2;
reg [W-1:0] arith_stg2_x;
reg [2*W-1:0] arith_x2;

// --- Stage 1 ---

always @(posedge clk) begin : arith_stage1
    arith_stg1_s <= x + y;
    arith_stg1_x <= x;
end

// --- Stage 2 ---

always @(posedge clk) begin : arith_stage2
    arith_stg2_s2 <= arith_stg1_s * arith_stg1_s;
    arith_stg2_x <= arith_stg1_x;
end

// --- Stage 3 ---

always @(posedge clk) begin : arith_stage3
    arith_x2 <= arith_stg2_x * arith_stg2_x;
    arith_s2 <= arith_stg2_s2;
end

// x2:arith_x2, s2:arith_s2

always @(*) begin
    out = arith_x2 - 1;
end

endmodule


