//----------------------------------------------------------------------------
// FA
//----------------------------------------------------------------------------
module FA (
    input a,
    input b,
    input cin,
    output reg s,
    output reg cout
);



always @(*) begin
    cout = a & b | a & cin | b & cin;
    s = a ^ b ^ cin;
end

endmodule

//----------------------------------------------------------------------------
// two_adders
//----------------------------------------------------------------------------
module two_adders (
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
    .a(a0),
    .b(b0),
    .cin(cin),
    .s(s0),
    .cout(c0)
);

FA  FA2 (
    .a(a1),
    .b(b1),
    .cin(c0),
    .s(s1),
    .cout(cout)
);

endmodule


