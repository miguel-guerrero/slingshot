//----------------------------------------------------------------------------
// counter
//----------------------------------------------------------------------------
module counter 
#(
    parameter WIDTH = 8)
(
    input clk,
    input rst_n,
    input clr,
    input inc,
    input [WIDTH-1:0] max_val,
    output reg [WIDTH-1:0] cnt,
    output reg eq
);



always @(*) begin
    eq = cnt == max_val;
end

// clear and increment logic
// goes here

always @(posedge clk or negedge rst_n) begin
    if (~rst_n) begin
        cnt <= 0;
    end
    else begin
        if (clr) begin
            // clear has priority
            cnt <= 0;
        end
        else if (inc) begin
            cnt <= cnt + 1;
        end
    end
end

endmodule


