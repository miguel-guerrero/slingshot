//----------------------------------------------------------------------------
// adder_WIDTH32
//----------------------------------------------------------------------------
module adder_WIDTH32 
#(
    parameter WIDTH = 32,
    parameter SWIDTH = WIDTH + 1)
(
    input cin,
    input [WIDTH-1:0] x,
    input [WIDTH-1:0] y,
    output reg [SWIDTH-1:0] sm,
    output reg [SWIDTH-1:0] sm_r,
    output reg sm_zero_r,
    input clk,
    input rst_n
);

reg [SWIDTH-1:0] res;

always @(*) begin : combo_logic
    res = x + y + cin;
    sm <= res;
end

always @(posedge clk or negedge rst_n) 
    if (~rst_n) begin
        sm_r <= 0;
        sm_zero_r <= 0;
    end
    else begin : registering
        sm_r <= sm;
        sm_zero_r <= sm == 0;
    end

endmodule
