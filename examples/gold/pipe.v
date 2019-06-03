//----------------------------------------------------------------------------
// pipe
//----------------------------------------------------------------------------
module pipe 
#(
    parameter W = 8)
(
    output reg [W+1:0] sad_res,
    output reg sad_vld,
    output reg sad_rdy,
    input clk,
    input rdy_dn,
    input rst_n,
    input vld_up,
    input [W-1:0] x0,
    input [W-1:0] x1,
    input [W-1:0] y0,
    input [W-1:0] y1
);

reg sad_stg0_vld;
reg signed [W:0] sad_stg1_dx;
reg signed [W:0] sad_stg1_dy;
reg sad_stg1_rdy;
reg sad_stg1_vld;
reg [W:0] sad_stg2_adx;
reg [W:0] sad_stg2_ady;
reg sad_stg2_rdy;
reg sad_stg2_vld;
reg sad_stg3_rdy;
reg sad_stg4_rdy;

// hook to upstream rdy

always @(*) begin
    sad_rdy <= sad_stg1_rdy;
end

// hook to upsstream vld

always @(*) begin
    sad_stg0_vld <= vld_up;
end

// --- Stage 1 ---

always @(posedge clk) begin : sad_stage1
    if (sad_stg0_vld & sad_stg1_rdy) begin
        sad_stg1_dx <= x1 - x0;
        sad_stg1_dy <= y1 - y0;
    end
end

always @(posedge clk or negedge rst_n) begin
    if (~rst_n) begin
        sad_stg1_vld <= 0;
    end
    else begin : sad_stage1_vld
        sad_stg1_vld <= sad_stg1_rdy ? sad_stg0_vld : sad_stg1_vld;
    end
end

always @(*) begin
    sad_stg1_rdy <= sad_stg2_rdy | ~sad_stg1_vld;
end

// --- Stage 2 ---

always @(posedge clk) begin : sad_stage2
    if (sad_stg1_vld & sad_stg2_rdy) begin
        sad_stg2_adx <= sad_stg1_dx < 0 ? -sad_stg1_dx : sad_stg1_dx;
        sad_stg2_ady <= sad_stg1_dy < 0 ? -sad_stg1_dy : sad_stg1_dy;
    end
end

always @(posedge clk or negedge rst_n) begin
    if (~rst_n) begin
        sad_stg2_vld <= 0;
    end
    else begin : sad_stage2_vld
        sad_stg2_vld <= sad_stg2_rdy ? sad_stg1_vld : sad_stg2_vld;
    end
end

always @(*) begin
    sad_stg2_rdy <= sad_stg3_rdy | ~sad_stg2_vld;
end

// --- Stage 3 ---

always @(posedge clk) begin : sad_stage3
    if (sad_stg2_vld & sad_stg3_rdy) begin
        sad_res <= sad_stg2_adx + sad_stg2_ady;
    end
end

always @(posedge clk or negedge rst_n) begin
    if (~rst_n) begin
        sad_vld <= 0;
    end
    else begin : sad_stage3_vld
        sad_vld <= sad_stg3_rdy ? sad_stg2_vld : sad_vld;
    end
end

always @(*) begin
    sad_stg3_rdy <= sad_stg4_rdy | ~sad_vld;
end

// hook to downstream rdy

always @(*) begin
    sad_stg4_rdy <= rdy_dn;
end

endmodule

