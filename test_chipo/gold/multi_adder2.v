//----------------------------------------------------------------------------
// adder
//----------------------------------------------------------------------------
module adder 
#(
    parameter SWIDTH = WIDTH + 1,
    parameter WIDTH = 8)
(
    input cin,
    input clk,
    input rst_n,
    input [WIDTH-1:0] x,
    input [WIDTH-1:0] y,
    output reg [SWIDTH-1:0] sm,
    output reg [SWIDTH-1:0] sm_r,
    output reg sm_zero_r
);

reg [SWIDTH-1:0] res;

always @(*) begin

    res = x + y + cin;
    sm <= res;
end

always @(posedge clk or negedge rst_n) 
    if (~rst_n) begin
        sm_r <= 0;
        sm_zero_r <= 0;
    end
    else begin
        sm_r <= sm;
        sm_zero_r <= sm == 0;
    end

endmodule

//----------------------------------------------------------------------------
// multi_adder_numAdders2
//----------------------------------------------------------------------------
module multi_adder_numAdders2 
#(
    parameter SWIDTH = WIDTH + 1,
    parameter WIDTH = 8)
(
    input cin_,
    input clk_,
    input rst_n_,
    input [7:0] x_,
    input [WIDTH-1:0] y,
    output [SWIDTH-1:0] sm,
    output [SWIDTH-1:0] sum0,
    output [SWIDTH-1:0] sum1
);



adder #(
    .WIDTH(WIDTH),
    .SWIDTH(SWIDTH)
) adder_0 (
    .cin(cin_),
    .clk(clk_),
    .rst_n(rst_n_),
    .x(x_),
    .y(y),
    .sm(sm),
    .sm_r(sum0),
    .sm_zero_r()
);

adder #(
    .WIDTH(WIDTH),
    .SWIDTH(SWIDTH)
) adder_1 (
    .cin(cin_),
    .clk(clk_),
    .rst_n(rst_n_),
    .x(x_),
    .y(y),
    .sm(sm),
    .sm_r(sum1),
    .sm_zero_r()
);

endmodule

