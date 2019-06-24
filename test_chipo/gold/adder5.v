//----------------------------------------------------------------------------
// adder
//----------------------------------------------------------------------------
module adder 
#(
    parameter WIDTH = 8,
    parameter SWIDTH = 9)
(
    output reg [SWIDTH-1:0] sm,
    input cin,
    input clk,
    input rst_n,
    input [WIDTH-1:0] x,
    input [WIDTH-1:0] y,
    output reg [SWIDTH-1:0] sm_r,
    output reg sm_zero_r
);

reg [SWIDTH-1:0] res;

always @(*) begin
    res = x + y + cin;
    if (res == 2) begin
        sm <= 1;
    end
    else begin
        sm <= res;
    end
end

always @(posedge clk or negedge rst_n) begin
    if (~rst_n) begin
        sm_r <= 0;
        sm_zero_r <= 0;
    end
    else begin
        if (~rst_n) begin
            sm_r <= 0;
            sm_zero_r <= 0;
        end
        else begin
            sm_r <= sm;
            sm_zero_r <= sm == 0;
        end
    end
end

endmodule


