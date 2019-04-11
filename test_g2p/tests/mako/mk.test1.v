<% 
N = passedParamDict.get("N", 32)
%>

module adder(
    input cin,
    input [${N}-1:0] a,
    input [${N}-1:0] b,
    output [${N}:0] sum
)

assign sum = a + b + cin;

endmodule
