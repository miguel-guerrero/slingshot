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
    output logic [2*W+1:0] arith_add_sqr,
    output logic [2*W-1:0] out
);

logic [W:0] arith_s1_add;
logic [W-1:0] arith_s1_x;
logic [2*W+1:0] arith_s2_add_sqr;
logic [W-1:0] arith_s2_x;
logic [2*W-1:0] arith_x_sqr;

// --- Stage 1 ---

always @(posedge clk) begin : arith_stage1
    arith_s1_add <= x + y;
    arith_s1_x <= x;
end

// --- Stage 2 ---

always @(posedge clk) begin : arith_stage2
    arith_s2_add_sqr <= arith_s1_add * arith_s1_add;
    arith_s2_x <= arith_s1_x;
end

// --- Stage 3 ---

always @(posedge clk) begin : arith_stage3
    arith_x_sqr <= arith_s2_x * arith_s2_x;
    arith_add_sqr <= arith_s2_add_sqr;
end

// x_sqr:arith_x_sqr, add_sqr:arith_add_sqr

assign out = arith_x_sqr - 1;

endmodule


