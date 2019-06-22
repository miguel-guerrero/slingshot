
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

parameter MEM_AW=16, MEM_DW=32, DIM_BITS=16, PREC=16;

wire mem_write, mem_req;
wire [MEM_AW-1:0] mem_addr;
wire [MEM_DW-1:0] mem_wdata;
wire mem_rdata_vld;
wire [MEM_DW-1:0] mem_rdata;

reg [MEM_AW-1:0] aBASE; 
reg [MEM_AW-1:0] bBASE; 
reg [MEM_AW-1:0] cBASE;
reg [DIM_BITS-1:0] aSTRIDE; 
reg [DIM_BITS-1:0] bSTRIDE; 
reg [DIM_BITS-1:0] cSTRIDE; 
reg [DIM_BITS-1:0] aROWS;
reg [DIM_BITS-1:0] aCOLS;
reg [DIM_BITS-1:0] bCOLS;

wire ret;
reg sm_ena;
reg go;
reg clk;
reg rst_n;

matmul #(.MEM_AW(MEM_AW), .MEM_DW(MEM_DW), .DIM_BITS(DIM_BITS), .PREC(PREC)) i_dut (.*); 
mem #(.MEM_AW(MEM_AW), .MEM_DW(MEM_DW)) i_mem (.*);

initial begin
    clk = 1;
    forever begin
        #5;
        clk = ~clk;
    end
end

initial begin
   #1; // allow dump to open 1st
   $display($time, " TEST starts");
   $display($time, " Reseting");
   go = 0;
   sm_ena = 1;
   i_mem.init_incr;
   aBASE = 'h100; 
   bBASE = 'h200;
   cBASE = 'h300;
   aROWS = 6;
   aCOLS = 4;
   bCOLS = 5;
   aSTRIDE = 4; //8;
   bSTRIDE = 5; //8; 
   cSTRIDE = 8; //5;
   rst_n = 0;
   #99;
   rst_n = 1;
   #500;
   $display($time, " Reseting");
   rst_n = 0;
   #100;
   rst_n = 1;
   #295;
   $display($time, " Start");
   go = 1;
   #105;
   go = 0;
   #300
   sm_ena = 0;
   #200
   sm_ena = 1;
   
   while (~ret)
       @(posedge clk);
   @(posedge clk);
   $display($time, " got ret");
   #100;

   // cut-n-paste output in matlab for debug
   $write("A="); 
   dump_mat(aBASE, aROWS, aCOLS, aSTRIDE);
   $write("B="); 
   dump_mat(bBASE, aCOLS, bCOLS, bSTRIDE);
   $write("C=");
   dump_mat(cBASE, aROWS, bCOLS, cSTRIDE);
   $display("Cg=A*B");
   $display("all(all(Cg==C))");

   begin: check
      integer i, j, k;
      reg [PREC-1:0] a;
      reg [PREC-1:0] b;
      reg [MEM_DW-1:0] acc, c;
      integer error_cnt;
      error_cnt=0;
      for (i=0; i<aROWS; i=i+1) begin
         for (j=0; j<bCOLS; j=j+1) begin
             acc = 0;
             for (k=0; k<aCOLS; k=k+1) begin
                a = i_mem.fast_read(aBASE + i*aSTRIDE+k);
                b = i_mem.fast_read(bBASE + k*bSTRIDE+j);
                acc = acc + a*b;
             end
             c = i_mem.fast_read(cBASE + i*cSTRIDE+j);
             if (acc != c) begin
                 $display("C[%d, %d]=gold(%d) dut(%d)", i, j, acc, c);
                 error_cnt = error_cnt + 1;
             end
         end
      end
      if (error_cnt != 0) begin
          $display($time, " ERRORS =%d", error_cnt);
      end else begin
          $display($time, " PASSED");
      end
   end

   $display($time, " ending");
   $finish;
end

task dump_mat;
   input [MEM_AW-1:0] BASE; 
   input [DIM_BITS-1:0] ROWS;
   input [DIM_BITS-1:0] COLS;
   input [DIM_BITS-1:0] STRIDE; 
   integer i, j;
   reg [MEM_DW-1:0] rdata;
   begin
      $display("["); 
      for (i=0; i<ROWS; i=i+1) begin
         for (j=0; j<COLS; j=j+1) begin
            rdata = i_mem.fast_read(BASE + i*STRIDE+j);
            $write(" %d ", rdata);
         end
         $display(";"); 
      end
      $display("]"); 
   end
endtask

always @(posedge clk) begin
   #0;
`ifdef GLS
   $display($time, " i=", i_dut.i , 
                   " j=", i_dut.j , 
                   " k=", i_dut.k , 
                   " acc=%x", acc);
`else
   $display($time, " i=", i_dut.i, 
                   " j=", i_dut.j, 
                   " k=", i_dut.k, 
                   " acc=%x", i_dut.acc);
`endif
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

initial begin
   #1000;
   repeat(1000 + aROWS*aCOLS*aROWS*bCOLS*10)
      @(posedge clk);

   $display($time, " ending timeout");
   $finish;
end

endmodule
