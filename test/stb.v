module stb;

reg clk;
initial begin
    clk = 0;
    forever begin
        #10;
        clk = ~clk;
    end
end

reg rst_n;
initial begin
    rst_n <= 1'b0;
    #100;
    rst_n <= 1'b1;
end

reg cin;
reg signed [7:0] x;
reg signed [7:0] y;
wire signed [7:0] sm, sm_r;
wire sm_zero_r;

adder adder_0 (.*);

`define tick @(posedge clk)
`define wait1(cond) `tick; while(~(cond)) `tick 


initial begin
    wait(rst_n == 1);
    `tick;
    $display($time, " ACTIVATING");
    x <= 'h11; y <= 'h22; cin <= 1'b1;
    `tick;
    x <= 1; y <= 255; cin <= 0;
    `tick;
    x <= 10; y <= 250; cin <= 0;
    `tick;
    x <= 0; y <= 0; cin <= 0;
    `tick;
    `tick;
    `tick;
    `tick;
    $finish;
end

initial forever begin
    `tick;
    $display($time, " x ", x, " y ", y, " cin ", cin,
                    " sm ", sm, " sm_r ", sm_r, " sm_zero_r ", sm_zero_r);
end

initial begin
    #2000;
    $display($time, " Time-out termination");
    $finish;
end

initial begin
    $dumpfile("tb.vcd");
end
endmodule
