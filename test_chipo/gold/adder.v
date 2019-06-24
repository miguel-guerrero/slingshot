//----------------------------------------------------------------------------
// adder
//----------------------------------------------------------------------------
module adder (
    input cin,
    input [7:0] x,
    input [7:0] y,
    output reg [8:0] sm,
    output reg [8:0] sm_r,
    output reg sm_zero_r,
    input clk,
    input rst_n
);



always @(*) begin : combo_logic
    sm = x + y + cin;
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


