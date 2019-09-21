//----------------------------------------------------------------------------
// FA
//----------------------------------------------------------------------------
module FA (
    input a,
    input b,
    input cin,
    output reg cout,
    output reg s
);




always @(*) begin
    s = a ^ b ^ cin;
    cout = a & b | a & cin | b & cin;
end


endmodule

//----------------------------------------------------------------------------
// multi_adder
//----------------------------------------------------------------------------
module multi_adder (
    input [7:0] a,
    input [7:0] b,
    input cin,
    output reg cout,
    output [7:0] s
);
wire [7:0] c; // auto



FA  FA1 (
    .a(a[0]),
    .b(b[0]),
    .cin(cin),
    .cout(c[0]),
    .s(s[0])
);

FA  FA2 (
    .a(a[1]),
    .b(b[1]),
    .cin(c[0]),
    .cout(c[1]),
    .s(s[1])
);

FA  FA3 (
    .a(a[2]),
    .b(b[2]),
    .cin(c[1]),
    .cout(c[2]),
    .s(s[2])
);

FA  FA4 (
    .a(a[3]),
    .b(b[3]),
    .cin(c[2]),
    .cout(c[3]),
    .s(s[3])
);

FA  FA5 (
    .a(a[4]),
    .b(b[4]),
    .cin(c[3]),
    .cout(c[4]),
    .s(s[4])
);

FA  FA6 (
    .a(a[5]),
    .b(b[5]),
    .cin(c[4]),
    .cout(c[5]),
    .s(s[5])
);

FA  FA7 (
    .a(a[6]),
    .b(b[6]),
    .cin(c[5]),
    .cout(c[6]),
    .s(s[6])
);

FA  FA8 (
    .a(a[7]),
    .b(b[7]),
    .cin(c[6]),
    .cout(c[7]),
    .s(s[7])
);
always @(*) cout = c[7];

endmodule


