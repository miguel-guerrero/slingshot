// passedParamDict {}

// defaultParamDict {'CNT': 8, 'WIDTH': 32, 'HAS_CIN': 0}
// paramDict {'HAS_CIN': 0, 'CNT': 8, 'WIDTH': 32, 'OWIDTH': 34}
// name adder_tree
// params.WIDTH 32
// params.OWIDTH 34
// params.HAS_CIN 0
// IOs [Output('sum', 34), Input('in0', 32), Input('in1', 32), Input('in2', 32), Input('in3', 32), Input('in4', 32), Input('in5', 32), Input('in6', 32), Input('in7', 32)]

module adder_tree
(
    output [33:0] sum,
    input [31:0] in0,
    input [31:0] in1,
    input [31:0] in2,
    input [31:0] in3,
    input [31:0] in4,
    input [31:0] in5,
    input [31:0] in6,
    input [31:0] in7
)


    wire [31:0] ps_0_0;
    adder adder_0_0 (
        .a(in0),
        .b(in1),
        .sum(ps_0_0)
    )


    wire [31:0] ps_0_1;
    adder adder_0_1 (
        .a(in2),
        .b(in3),
        .sum(ps_0_1)
    )


    wire [31:0] ps_0_2;
    adder adder_0_2 (
        .a(in4),
        .b(in5),
        .sum(ps_0_2)
    )


    wire [31:0] ps_0_3;
    adder adder_0_3 (
        .a(in6),
        .b(in7),
        .sum(ps_0_3)
    )


    wire [32:0] ps_1_0;
    adder_WIDTH33 adder_1_0 (
        .a(ps_0_0),
        .b(ps_0_1),
        .sum(ps_1_0)
    )


    wire [32:0] ps_1_1;
    adder_WIDTH33 adder_1_1 (
        .a(ps_0_2),
        .b(ps_0_3),
        .sum(ps_1_1)
    )


    wire [33:0] ps_2_0;
    adder_WIDTH34 adder_2_0 (
        .a(ps_1_0),
        .b(ps_1_1),
        .sum(ps_2_0)
    )


assign sum = ps_2_0;

endmodule

