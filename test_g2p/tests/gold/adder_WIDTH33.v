




// passedParamDict {'WIDTH': 33}


// defaultParamDict {'WIDTH': 32, 'HAS_CIN': 0}
// paramDict {'HAS_CIN': 0, 'WIDTH': 33}
// name adder_WIDTH33
// params.WIDTH 33
// params.HAS_CIN 0
// IOs [Input('a', 33), Input('b', 33), Output('sum', 34)]

module adder_WIDTH33
(
    input [32:0] a,
    input [32:0] b,
    output [33:0] sum
)

assign sum = a + b
           ;
endmodule

// userResult.area = 33
