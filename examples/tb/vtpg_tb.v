
module tb;

parameter PW=8, H_BITS=12, V_BITS=12;
wire hs;
wire vs;
wire [3*PW-1:0] rgb;
wire rgb_vld;
wire [H_BITS-1:0] tHS_START = 10;
wire [H_BITS-1:0] tHS_END = 20;
wire [H_BITS-1:0] tHACT_START = 40;
wire [H_BITS-1:0] tHACT_END = 50;
wire [H_BITS-1:0] tH_END =60;
wire [V_BITS-1:0] tVS_START = 11;
wire [V_BITS-1:0] tVS_END = 21;
wire [V_BITS-1:0] tVACT_START = 25;
wire [V_BITS-1:0] tVACT_END = 35;
wire [H_BITS-1:0] tV_END = 40;
reg clk;
reg rst_n;

vtpg 
#(.PW(PW), .H_BITS(H_BITS), .V_BITS(V_BITS)) 
i_dut(.*);

initial begin
    clk = 0;
    forever begin
        #10;
        clk = ~clk;
    end
end

initial begin
   #1;
   $display($time, " TEST starts");
   $display($time, " Reseting");
   rst_n = 0;
   repeat(4) @(posedge clk);
   rst_n = 1;
   $display($time, " Reset deasserted");
   repeat(125) @(posedge clk);
   $display($time, " Reseting");
   rst_n = 0;
   repeat(2) @(posedge clk);
   rst_n = 1;
   $display($time, " Reset deasserted");
end

always @(negedge clk) begin
   $display($time, " hs=", hs, " vs=", vs, " vld=", rgb_vld, " rgb=%x", rgb);
end

initial begin
   $dumpfile("tb.vcd");
   $dumpvars;
end

initial begin
   #1000;
   repeat(1000 + (1+tH_END)*(1+tV_END)) 
      @(posedge clk);
   $display($time, " ending");
   $finish;
end

endmodule
