




// passedParamDict {'WIDTH': 35}


// defaultParamDict {'WIDTH': 32, 'HAS_CIN': 0}
// paramDict {'HAS_CIN': 0, 'WIDTH': 35}
// name adder_WIDTH35
// params.WIDTH 35
// params.HAS_CIN 0
// IOs [Input('a', 35), Input('b', 35), Output('sum', 36)]

module adder_WIDTH35
(
    input [34:0] a,
    input [34:0] b,
    output [35:0] sum
)

assign sum = a + b
           ;
endmodule

// userResult.area = 35
