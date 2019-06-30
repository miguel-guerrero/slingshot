module pipe_tb;

parameter W=8;
parameter CLK_HALF_PERIOD=5;

`ifndef NITERS
 `define NITERS 1000
`endif

`ifdef FIXED_VLD
 `define FIXED_VLD 1
`else
 `define FIXED_VLD 0
`endif

`ifdef FIXED_RDY
 `define FIXED_RDY 1
`else
 `define FIXED_RDY 0
`endif

`ifndef SEED
 `define SEED 1
`endif

reg clk;
initial begin
    clk = 1;
    forever begin
        #CLK_HALF_PERIOD;
        clk = ~clk;
    end
end

reg rst_n;
initial begin
    rst_n <= 1'b0;
    #(10*CLK_HALF_PERIOD);
    rst_n <= 1'b1;
end

reg [W-1:0] x0;
reg [W-1:0] x1;
reg [W-1:0] y0;
reg [W-1:0] y1;
wire [W+1:0] sad_res;
wire zero;

reg vld_up;
wire sad_rdy;

wire sad_vld;
reg rdy_dn;

pipe #(W) pipe_0 (.*);

`define tick @(posedge clk)
`define ntick @(negedge clk)
`define wait1(cond) `tick; while(~(cond)) `tick 
`define SD #1


integer i, iter;
reg [31:0] r;
reg [31:0] seed;
initial begin : source
    seed = `SEED;
    vld_up = 0;
    wait(rst_n == 1);
    `tick;
    $display($time, " ACTIVATING");
    for (iter=0; iter<`NITERS; iter=iter+1) begin
        for (i=0; i<80; i=i+1) begin
            x0 <= `SD i;
            x1 <= `SD i+1;
            y0 <= `SD 3*i;
            y1 <= `SD 2*i;
            do begin
                r = $random(seed);
                vld_up <= `SD `FIXED_VLD | (r[3:0] < 12); // prob 12/16 = 0.75
                `tick;
            end while (~(sad_rdy & vld_up));
        end
    end
    `tick;
    `tick;
    $display("RESULT: PASS");
    $finish;
end

initial begin : sink_stall
    reg [31:0] r;
    rdy_dn = 1;
    wait(rst_n == 1);
    `tick;
    forever begin
        `tick;
        r = $random(seed);
        rdy_dn <= `SD `FIXED_RDY | (r[2:0] < 2); // prob 2/8 = 0.25
    end
end

integer j;
initial begin : monitor
    reg [W-1:0] exp_sad;
    j=0;
    forever begin
        `ntick;
        if (sad_vld && rdy_dn) begin
            $display($time, " sad_res ", sad_res);
            exp_sad = (1+j);
            if (sad_res != exp_sad) begin
                $display($time, " ERROR: exp_sad ", exp_sad);
                $display("RESULT: FAIL");
                `ntick;
                `ntick;
                $finish;
            end
            j = (j+1) % 80;
        end
    end
end

initial begin : time_out
    #(1000*2*CLK_HALF_PERIOD*`NITERS);
    $display($time, " Time-out termination");
    $display("RESULT: FAIL");
    $finish;
end

initial begin
    $dumpfile("tb.vcd");
`ifdef DUMP
    $dumpvars;
`endif
end

endmodule
