




// passedParamDict {'WIDTH': 32}


// defaultParamDict {'WIDTH': 32, 'HAS_CIN': 0}
// paramDict {'HAS_CIN': 0, 'WIDTH': 32}
// name adder
// params.WIDTH 32
// params.HAS_CIN 0
// IOs [Input('a', 32), Input('b', 32), Output('sum', 33)]

module adder
(
    input [31:0] a,
    input [31:0] b,
    output [32:0] sum
)

assign sum = a + b
           ;
endmodule

// userResult.area = 32
