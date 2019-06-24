//----------------------------------------------------------------------------
// adder
//----------------------------------------------------------------------------
module adder 
#(
    parameter W = 8)
(
    input cin,
    input clk,
    input [4*W-1:0] ins,
    input rst_n,
    output reg [W+1:0] sm,
    output reg [W+1:0] sm_r,
    output reg sm_zero_r
);



always @(*) begin : combo_logic
    sm = ins/*.x*/[W-1:0] + ins/*.y*/[2*W-1:W] + ins/*.z*/[3*W-1:2*W] + ins/*.w*/[4*W-1:3*W] + cin;
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


