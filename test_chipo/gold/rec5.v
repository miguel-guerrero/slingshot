//----------------------------------------------------------------------------
// adder
//----------------------------------------------------------------------------
module adder (
    input clk,
    input [32:0] ins,
    input rst_n,
    output reg [9:0] sm,
    output reg [9:0] sm_r,
    output reg sm_zero_r
);

reg [7:0] x;

always @(*) begin : combo_logic
    x = ins/*.s1.x*/[7:0];
    sm <= x[3:2] + ins/*.s1.y*/[15:8] + ins/*.s1.z*/[23:16] + ins/*.s1.w*/[31:24] + ins/*.cin*/[32];
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
