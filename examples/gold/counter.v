//----------------------------------------------------------------------------
// counter
//----------------------------------------------------------------------------
module counter 
#(
    parameter WIDTH = 8)
(
    input clk,
    input clr,
    input inc,
    input [WIDTH-1:0] max_val,
    input rst_n,
    output reg [WIDTH-1:0] cnt,
    output reg eq
);



always @(*) 
    eq <= cnt == max_val;

// clear and increment logic
// goes here

always @(posedge clk or negedge rst_n) 
    if (~rst_n) 
        cnt <= 0;
    else 
        if (clr) begin
            // clear has priority
            cnt <= 0;
        end
        else if (inc) 
            cnt <= cnt + 1;

endmodule

