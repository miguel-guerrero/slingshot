//----------------------------------------------------------------------------
// adder
//----------------------------------------------------------------------------
module adder 
#(
    parameter WIDTH = 8,
    parameter SWIDTH = WIDTH)
(
    input cin,
    input signed [WIDTH-1:0] x,
    input signed [WIDTH-1:0] y,
    output reg signed [SWIDTH-1:0] sm,
    output reg signed [SWIDTH-1:0] sm_r,
    output reg sm_zero_r,
    input clk,
    input rst_n
);

reg signed [SWIDTH-1:0] res;

always @(*) begin : combo_logic
    res = x + y + cin;
    sm <= res;
end

always @(posedge clk or negedge rst_n) begin
    if (~rst_n) begin
        sm_r <= 0;
        sm_zero_r <= 0;
    end
    else begin : registering
        sm_r <= sm;
        sm_zero_r <= sm == 0;
    end
end

endmodule


