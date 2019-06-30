//----------------------------------------------------------------------------
// FA
//----------------------------------------------------------------------------
module FA (
    input cin,
    input a,
    input b,
    output reg s,
    output reg cout
);



always @(*) begin
    s = a ^ b ^ cin;
    cout = a & b | a & cin | b & cin;
end

endmodule

//----------------------------------------------------------------------------
// two_adder
//----------------------------------------------------------------------------
module two_adder (
    input a0,
    input a1,
    input b0,
    input b1,
    input cin,
    output cout,
    output s0,
    output s1
);
wire c0; // auto


FA  FA1 (
    .cin(cin),
    .a(a0),
    .b(b0),
    .s(s0),
    .cout(c0)
);

FA  FA2 (
    .cin(c0),
    .a(a1),
    .b(b1),
    .s(s1),
    .cout(cout)
);

endmodule


