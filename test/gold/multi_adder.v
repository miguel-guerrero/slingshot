//----------------------------------------------------------------------------
// adder
//----------------------------------------------------------------------------
module adder 
#(
    parameter WIDTH = 8,
    parameter SWIDTH = WIDTH + 1)
(
    input cin,
    input clk,
    input rst_n,
    input [WIDTH-1:0] x,
    input [WIDTH-1:0] y,
    output [SWIDTH-1:0] sm,
    output [SWIDTH-1:0] sm_r,
    output sm_zero_r
);

reg [SWIDTH-1:0] res;
reg [SWIDTH-1:0] sm;
reg [SWIDTH-1:0] sm_r;
reg sm_zero_r;

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

//----------------------------------------------------------------------------
// multi_adder
//----------------------------------------------------------------------------
module multi_adder 
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
    output [SWIDTH-1:0] sm_r,
    output sm_zero_r
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
    .sm_r(sm_r),
    .sm_zero_r(sm_zero_r)
);

endmodule

