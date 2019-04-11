




// passedParamDict {'WIDTH': 34}


// defaultParamDict {'WIDTH': 32, 'HAS_CIN': 0}
// paramDict {'HAS_CIN': 0, 'WIDTH': 34}
// name adder_WIDTH34
// params.WIDTH 34
// params.HAS_CIN 0
// IOs [Input('a', 34), Input('b', 34), Output('sum', 35)]

module adder_WIDTH34
(
    input [33:0] a,
    input [33:0] b,
    output [34:0] sum
)

assign sum = a + b
           ;
endmodule

// userResult.area = 34
