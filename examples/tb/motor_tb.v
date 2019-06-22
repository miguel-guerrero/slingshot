

module tb;

`ifdef BEHAV
    initial $display("#RUNNING BEHAVIORAL code");
`else
   `ifdef GLS
        initial $display("#RUNNING GLS code");
   `else
        initial $display("#RUNNING RTL code");
   `endif
`endif

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

`define tick @(posedge clk)
`define wait1(cond) `tick; while(~(cond)) `tick 

wire [1:0] control_state;
reg activate, up_limit, dn_limit;
wire motor_up_q, motor_dn_q;

motor_fsm motor_0 (.*);

initial begin
    activate <= 0;
    up_limit <= 1; // door is up
    dn_limit <= 0;
    wait(rst_n == 1);
    `tick;
    $display($time, " ACTIVATING");
    activate <= 1;
    `wait1(motor_dn_q == 1);
    activate <= 0;
    up_limit <= 0;
    `tick;
    `tick;
    `tick;
    `tick;
    $display($time, " REPORTING dn_limit");
    dn_limit <= 1;
    `wait1(motor_dn_q == 0);
    `tick;

    $display($time, " ACTIVATING");
    activate <= 1;
    `wait1(motor_up_q == 1);
    activate <= 0;
    dn_limit <= 0;
    `tick;
    `tick;
    `tick;
    `tick;
    `tick;
    `tick;
    $display($time, " REPORTING up_limit");
    up_limit <= 1;
    `wait1(motor_up_q == 0);
    `tick;

    $display($time, " Normal termination");
    $finish;
end

initial forever begin
    `tick;
    $display($time, " activate ", activate, " up_limit ", up_limit, " dn_limit ", dn_limit,
                    " motor_dn ", motor_dn_q, " motor_up ", motor_up_q);
end

initial begin
    #2000;
    $display($time, " Time-out termination");
    $finish;
end

initial begin
`ifdef BEHAV
    $dumpfile("tb_beh.vcd");
`else
    `ifdef GLS
        $dumpfile("tb_gls.vcd");
    `else
        $dumpfile("tb.vcd");
    `endif
`endif
    $dumpvars;
end

endmodule
