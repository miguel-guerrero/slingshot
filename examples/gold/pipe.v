//----------------------------------------------------------------------------
// pipe
//----------------------------------------------------------------------------
module pipe 
#(
    parameter W = 8)
(
    output logic [W+1:0] sad_res,
    output logic sad_vld,
    output logic sad_rdy,
    input clk,
    input rdy_dn,
    input rst_n,
    input vld_up,
    input [W-1:0] x0,
    input [W-1:0] x1,
    input [W-1:0] y0,
    input [W-1:0] y1
);

logic sad_s0_vld;
logic signed [W:0] sad_s1_dx;
logic signed [W:0] sad_s1_dy;
logic sad_s1_rdy;
logic sad_s1_vld;
logic [W:0] sad_s2_adx;
logic [W:0] sad_s2_ady;
logic sad_s2_rdy;
logic sad_s2_vld;
logic sad_s3_rdy;
logic sad_s4_rdy;

// hook to upstream rdy

assign sad_rdy = sad_s1_rdy;

// hook to upsstream vld

assign sad_s0_vld = vld_up;

// --- Stage 1 ---

always @(posedge clk) begin : sad_stage1
    if (sad_s0_vld & sad_s1_rdy) begin
        sad_s1_dx <= x1 - x0;
        sad_s1_dy <= y1 - y0;
    end
end

always @(posedge clk or negedge rst_n) begin : sad_stage1_vld
    if (~rst_n) begin
        sad_s1_vld <= 0;
    end
    else begin
        sad_s1_vld <= sad_s1_rdy ? sad_s0_vld : sad_s1_vld;
    end
end

assign sad_s1_rdy = sad_s2_rdy | ~sad_s1_vld;

// --- Stage 2 ---

always @(posedge clk) begin : sad_stage2
    if (sad_s1_vld & sad_s2_rdy) begin
        sad_s2_adx <= sad_s1_dx < 0 ? -sad_s1_dx : sad_s1_dx;
        sad_s2_ady <= sad_s1_dy < 0 ? -sad_s1_dy : sad_s1_dy;
    end
end

always @(posedge clk or negedge rst_n) begin : sad_stage2_vld
    if (~rst_n) begin
        sad_s2_vld <= 0;
    end
    else begin
        sad_s2_vld <= sad_s2_rdy ? sad_s1_vld : sad_s2_vld;
    end
end

assign sad_s2_rdy = sad_s3_rdy | ~sad_s2_vld;

// --- Stage 3 ---

always @(posedge clk) begin : sad_stage3
    if (sad_s2_vld & sad_s3_rdy) begin
        sad_res <= sad_s2_adx + sad_s2_ady;
    end
end

always @(posedge clk or negedge rst_n) begin : sad_stage3_vld
    if (~rst_n) begin
        sad_vld <= 0;
    end
    else begin
        sad_vld <= sad_s3_rdy ? sad_s2_vld : sad_vld;
    end
end

assign sad_s3_rdy = sad_s4_rdy | ~sad_vld;

// hook to downstream rdy

assign sad_s4_rdy = rdy_dn;

endmodule


