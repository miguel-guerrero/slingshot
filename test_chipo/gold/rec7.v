//----------------------------------------------------------------------------
// adder
//----------------------------------------------------------------------------
module adder (
    input clk,
    input rst_n,
    output reg [9:0] sm,
    output reg [9:0] sm_r,
    output reg sm_zero_r
);

reg [32:0] ins;


always @(*) begin : combo_logic
    sm <= ins/*.s1.x*/[7:0] + ins/*.s1.y[3:2]*/[11:10] + ins/*.s1.z*/[23:16] + ins/*.s1.w*/[31:24] + ins/*.cin*/[32];
    ins/*.s1.x*/[7:0] <= ins/*.s1.y*/[15:8];
end


always @(posedge clk or negedge rst_n) begin : registering
    if (~rst_n) begin
        sm_r <= 0;
        sm_zero_r <= 0;
    end
    else begin
        sm_r <= sm;
        sm_zero_r <= sm == 0;
    end
end


endmodule


