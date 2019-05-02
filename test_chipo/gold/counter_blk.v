
//----------------------------------------------------------------------------
// debug_apb_csr_wrap
//----------------------------------------------------------------------------
module debug_apb_csr_wrap (
    input [31:0] PADDR,
    input PENABLE,
    input PSEL,
    input [31:0] PWDATA,
    input PWRITE,
    input clk,
    input [39:0] cnt0_val,
    input [39:0] cnt10_val,
    input [39:0] cnt11_val,
    input [39:0] cnt1_val,
    input [39:0] cnt2_val,
    input [39:0] cnt3_val,
    input [39:0] cnt4_val,
    input [39:0] cnt5_val,
    input [39:0] cnt6_val,
    input [39:0] cnt7_val,
    input [39:0] cnt8_val,
    input [39:0] cnt9_val,
    input rst_n,
    output [31:0] PRDATA,
    output PREADY,
    output PSLVERR,
    output [15:0] chain_tc,
    output [11:0] clr_sel_mode_any,
    output [31:0] clr_tc_mask0,
    output [31:0] clr_tc_mask1,
    output [31:0] clr_tc_mask2,
    output [31:0] clr_tc_mask3,
    output [31:0] clr_tc_mask4,
    output [31:0] clr_tc_mask5,
    output [31:0] clr_tc_mask6,
    output [31:0] clr_tc_mask7,
    output [31:0] clr_tc_mask8,
    output [31:0] clr_tc_mask9,
    output [31:0] clr_tc_mask10,
    output [31:0] clr_tc_mask11,
    output [11:0] inc_sel_mode_any,
    output [31:0] inc_tc_mask0,
    output [31:0] inc_tc_mask1,
    output [31:0] inc_tc_mask2,
    output [31:0] inc_tc_mask3,
    output [31:0] inc_tc_mask4,
    output [31:0] inc_tc_mask5,
    output [31:0] inc_tc_mask6,
    output [31:0] inc_tc_mask7,
    output [31:0] inc_tc_mask8,
    output [31:0] inc_tc_mask9,
    output [31:0] inc_tc_mask10,
    output [31:0] inc_tc_mask11,
    output [39:0] max_val0_val,
    output [39:0] max_val10_val,
    output [39:0] max_val11_val,
    output [39:0] max_val1_val,
    output [39:0] max_val2_val,
    output [39:0] max_val3_val,
    output [39:0] max_val4_val,
    output [39:0] max_val5_val,
    output [39:0] max_val6_val,
    output [39:0] max_val7_val,
    output [39:0] max_val8_val,
    output [39:0] max_val9_val,
    output [31:0] rel_mask0,
    output [31:0] rel_mask1,
    output [31:0] rel_mask2,
    output [31:0] rel_mask3,
    output [31:0] rel_mask4,
    output [31:0] rel_mask5,
    output [31:0] rel_mask6,
    output [31:0] rel_mask7,
    output [31:0] rel_mask8,
    output [31:0] rel_mask9,
    output [31:0] rel_mask10,
    output [31:0] rel_mask11,
    output [31:0] rel_mask12,
    output [31:0] rel_mask13,
    output [31:0] rel_mask14,
    output [31:0] rel_mask15,
    output [31:0] rel_mask16,
    output [31:0] rel_mask17,
    output [31:0] rel_mask18,
    output [31:0] rel_mask19,
    output [31:0] rel_mask20,
    output [31:0] rel_mask21,
    output [31:0] rel_mask22,
    output [31:0] rel_mask23,
    output [31:0] rel_mask24,
    output [31:0] rel_mask25,
    output [31:0] rel_mask26,
    output [31:0] rel_mask27,
    output [31:0] rel_mask28,
    output [31:0] rel_mask29,
    output [31:0] rel_mask30,
    output [31:0] rel_mask31,
    output [31:0] sel_delta,
    output [31:0] trig_inv,
    output [31:0] val_mask0,
    output [31:0] val_mask1,
    output [31:0] val_mask2,
    output [31:0] val_mask3,
    output [31:0] val_mask4,
    output [31:0] val_mask5,
    output [31:0] val_mask6,
    output [31:0] val_mask7,
    output [31:0] val_mask8,
    output [31:0] val_mask9,
    output [31:0] val_mask10,
    output [31:0] val_mask11,
    output [31:0] val_mask12,
    output [31:0] val_mask13,
    output [31:0] val_mask14,
    output [31:0] val_mask15,
    output [31:0] val_mask16,
    output [31:0] val_mask17,
    output [31:0] val_mask18,
    output [31:0] val_mask19,
    output [31:0] val_mask20,
    output [31:0] val_mask21,
    output [31:0] val_mask22,
    output [31:0] val_mask23,
    output [31:0] val_mask24,
    output [31:0] val_mask25,
    output [31:0] val_mask26,
    output [31:0] val_mask27,
    output [31:0] val_mask28,
    output [31:0] val_mask29,
    output [31:0] val_mask30,
    output [31:0] val_mask31
);
wire [31:0] max_val0_r0_val_f0; // auto
wire [7:0] max_val0_r1_val_f1; // auto
wire [31:0] max_val10_r0_val_f0; // auto
wire [7:0] max_val10_r1_val_f1; // auto
wire [31:0] max_val11_r0_val_f0; // auto
wire [7:0] max_val11_r1_val_f1; // auto
wire [31:0] max_val1_r0_val_f0; // auto
wire [7:0] max_val1_r1_val_f1; // auto
wire [31:0] max_val2_r0_val_f0; // auto
wire [7:0] max_val2_r1_val_f1; // auto
wire [31:0] max_val3_r0_val_f0; // auto
wire [7:0] max_val3_r1_val_f1; // auto
wire [31:0] max_val4_r0_val_f0; // auto
wire [7:0] max_val4_r1_val_f1; // auto
wire [31:0] max_val5_r0_val_f0; // auto
wire [7:0] max_val5_r1_val_f1; // auto
wire [31:0] max_val6_r0_val_f0; // auto
wire [7:0] max_val6_r1_val_f1; // auto
wire [31:0] max_val7_r0_val_f0; // auto
wire [7:0] max_val7_r1_val_f1; // auto
wire [31:0] max_val8_r0_val_f0; // auto
wire [7:0] max_val8_r1_val_f1; // auto
wire [31:0] max_val9_r0_val_f0; // auto
wire [7:0] max_val9_r1_val_f1; // auto
reg [31:0] cnt0_r0_val_f0;
reg [7:0] cnt0_r1_val_f1;
reg [31:0] cnt10_r0_val_f0;
reg [7:0] cnt10_r1_val_f1;
reg [31:0] cnt11_r0_val_f0;
reg [7:0] cnt11_r1_val_f1;
reg [31:0] cnt1_r0_val_f0;
reg [7:0] cnt1_r1_val_f1;
reg [31:0] cnt2_r0_val_f0;
reg [7:0] cnt2_r1_val_f1;
reg [31:0] cnt3_r0_val_f0;
reg [7:0] cnt3_r1_val_f1;
reg [31:0] cnt4_r0_val_f0;
reg [7:0] cnt4_r1_val_f1;
reg [31:0] cnt5_r0_val_f0;
reg [7:0] cnt5_r1_val_f1;
reg [31:0] cnt6_r0_val_f0;
reg [7:0] cnt6_r1_val_f1;
reg [31:0] cnt7_r0_val_f0;
reg [7:0] cnt7_r1_val_f1;
reg [31:0] cnt8_r0_val_f0;
reg [7:0] cnt8_r1_val_f1;
reg [31:0] cnt9_r0_val_f0;
reg [7:0] cnt9_r1_val_f1;
reg [39:0] max_val0_val;
reg [39:0] max_val10_val;
reg [39:0] max_val11_val;
reg [39:0] max_val1_val;
reg [39:0] max_val2_val;
reg [39:0] max_val3_val;
reg [39:0] max_val4_val;
reg [39:0] max_val5_val;
reg [39:0] max_val6_val;
reg [39:0] max_val7_val;
reg [39:0] max_val8_val;
reg [39:0] max_val9_val;

always @(*) 
    max_val0_val <= {
        max_val0_r1_val_f1,
        max_val0_r0_val_f0};

always @(*) 
    max_val1_val <= {
        max_val1_r1_val_f1,
        max_val1_r0_val_f0};

always @(*) 
    max_val2_val <= {
        max_val2_r1_val_f1,
        max_val2_r0_val_f0};

always @(*) 
    max_val3_val <= {
        max_val3_r1_val_f1,
        max_val3_r0_val_f0};

always @(*) 
    max_val4_val <= {
        max_val4_r1_val_f1,
        max_val4_r0_val_f0};

always @(*) 
    max_val5_val <= {
        max_val5_r1_val_f1,
        max_val5_r0_val_f0};

always @(*) 
    max_val6_val <= {
        max_val6_r1_val_f1,
        max_val6_r0_val_f0};

always @(*) 
    max_val7_val <= {
        max_val7_r1_val_f1,
        max_val7_r0_val_f0};

always @(*) 
    max_val8_val <= {
        max_val8_r1_val_f1,
        max_val8_r0_val_f0};

always @(*) 
    max_val9_val <= {
        max_val9_r1_val_f1,
        max_val9_r0_val_f0};

always @(*) 
    max_val10_val <= {
        max_val10_r1_val_f1,
        max_val10_r0_val_f0};

always @(*) 
    max_val11_val <= {
        max_val11_r1_val_f1,
        max_val11_r0_val_f0};

always @(*) 
    {
    cnt0_r1_val_f1,
    cnt0_r0_val_f0} <= cnt0_val;

always @(*) 
    {
    cnt1_r1_val_f1,
    cnt1_r0_val_f0} <= cnt1_val;

always @(*) 
    {
    cnt2_r1_val_f1,
    cnt2_r0_val_f0} <= cnt2_val;

always @(*) 
    {
    cnt3_r1_val_f1,
    cnt3_r0_val_f0} <= cnt3_val;

always @(*) 
    {
    cnt4_r1_val_f1,
    cnt4_r0_val_f0} <= cnt4_val;

always @(*) 
    {
    cnt5_r1_val_f1,
    cnt5_r0_val_f0} <= cnt5_val;

always @(*) 
    {
    cnt6_r1_val_f1,
    cnt6_r0_val_f0} <= cnt6_val;

always @(*) 
    {
    cnt7_r1_val_f1,
    cnt7_r0_val_f0} <= cnt7_val;

always @(*) 
    {
    cnt8_r1_val_f1,
    cnt8_r0_val_f0} <= cnt8_val;

always @(*) 
    {
    cnt9_r1_val_f1,
    cnt9_r0_val_f0} <= cnt9_val;

always @(*) 
    {
    cnt10_r1_val_f1,
    cnt10_r0_val_f0} <= cnt10_val;

always @(*) 
    {
    cnt11_r1_val_f1,
    cnt11_r0_val_f0} <= cnt11_val;

debug_apb_csr  debug_apb_csr_0 (
    .PCLK(clk),
    .PRESETN(rst_n),
    .PSEL(PSEL),
    .PENABLE(PENABLE),
    .PWRITE(PWRITE),
    .PADDR(PADDR),
    .PWDATA(PWDATA),
    .cnt0_r0_val_f0(cnt0_r0_val_f0),
    .cnt0_r1_val_f1(cnt0_r1_val_f1),
    .cnt1_r0_val_f0(cnt1_r0_val_f0),
    .cnt1_r1_val_f1(cnt1_r1_val_f1),
    .cnt2_r0_val_f0(cnt2_r0_val_f0),
    .cnt2_r1_val_f1(cnt2_r1_val_f1),
    .cnt3_r0_val_f0(cnt3_r0_val_f0),
    .cnt3_r1_val_f1(cnt3_r1_val_f1),
    .cnt4_r0_val_f0(cnt4_r0_val_f0),
    .cnt4_r1_val_f1(cnt4_r1_val_f1),
    .cnt5_r0_val_f0(cnt5_r0_val_f0),
    .cnt5_r1_val_f1(cnt5_r1_val_f1),
    .cnt6_r0_val_f0(cnt6_r0_val_f0),
    .cnt6_r1_val_f1(cnt6_r1_val_f1),
    .cnt7_r0_val_f0(cnt7_r0_val_f0),
    .cnt7_r1_val_f1(cnt7_r1_val_f1),
    .cnt8_r0_val_f0(cnt8_r0_val_f0),
    .cnt8_r1_val_f1(cnt8_r1_val_f1),
    .cnt9_r0_val_f0(cnt9_r0_val_f0),
    .cnt9_r1_val_f1(cnt9_r1_val_f1),
    .cnt10_r0_val_f0(cnt10_r0_val_f0),
    .cnt10_r1_val_f1(cnt10_r1_val_f1),
    .cnt11_r0_val_f0(cnt11_r0_val_f0),
    .cnt11_r1_val_f1(cnt11_r1_val_f1),
    .PRDATA(PRDATA),
    .PREADY(PREADY),
    .PSLVERR(PSLVERR),
    .chain_tc_val(chain_tc),
    .clr_sel_mode_any_val(clr_sel_mode_any),
    .clr_tc_mask0_val(clr_tc_mask0),
    .clr_tc_mask1_val(clr_tc_mask1),
    .clr_tc_mask2_val(clr_tc_mask2),
    .clr_tc_mask3_val(clr_tc_mask3),
    .clr_tc_mask4_val(clr_tc_mask4),
    .clr_tc_mask5_val(clr_tc_mask5),
    .clr_tc_mask6_val(clr_tc_mask6),
    .clr_tc_mask7_val(clr_tc_mask7),
    .clr_tc_mask8_val(clr_tc_mask8),
    .clr_tc_mask9_val(clr_tc_mask9),
    .clr_tc_mask10_val(clr_tc_mask10),
    .clr_tc_mask11_val(clr_tc_mask11),
    .inc_sel_mode_any_val(inc_sel_mode_any),
    .inc_tc_mask0_val(inc_tc_mask0),
    .inc_tc_mask1_val(inc_tc_mask1),
    .inc_tc_mask2_val(inc_tc_mask2),
    .inc_tc_mask3_val(inc_tc_mask3),
    .inc_tc_mask4_val(inc_tc_mask4),
    .inc_tc_mask5_val(inc_tc_mask5),
    .inc_tc_mask6_val(inc_tc_mask6),
    .inc_tc_mask7_val(inc_tc_mask7),
    .inc_tc_mask8_val(inc_tc_mask8),
    .inc_tc_mask9_val(inc_tc_mask9),
    .inc_tc_mask10_val(inc_tc_mask10),
    .inc_tc_mask11_val(inc_tc_mask11),
    .max_val0_r0_val_f0(max_val0_r0_val_f0),
    .max_val0_r1_val_f1(max_val0_r1_val_f1),
    .max_val1_r0_val_f0(max_val1_r0_val_f0),
    .max_val1_r1_val_f1(max_val1_r1_val_f1),
    .max_val2_r0_val_f0(max_val2_r0_val_f0),
    .max_val2_r1_val_f1(max_val2_r1_val_f1),
    .max_val3_r0_val_f0(max_val3_r0_val_f0),
    .max_val3_r1_val_f1(max_val3_r1_val_f1),
    .max_val4_r0_val_f0(max_val4_r0_val_f0),
    .max_val4_r1_val_f1(max_val4_r1_val_f1),
    .max_val5_r0_val_f0(max_val5_r0_val_f0),
    .max_val5_r1_val_f1(max_val5_r1_val_f1),
    .max_val6_r0_val_f0(max_val6_r0_val_f0),
    .max_val6_r1_val_f1(max_val6_r1_val_f1),
    .max_val7_r0_val_f0(max_val7_r0_val_f0),
    .max_val7_r1_val_f1(max_val7_r1_val_f1),
    .max_val8_r0_val_f0(max_val8_r0_val_f0),
    .max_val8_r1_val_f1(max_val8_r1_val_f1),
    .max_val9_r0_val_f0(max_val9_r0_val_f0),
    .max_val9_r1_val_f1(max_val9_r1_val_f1),
    .max_val10_r0_val_f0(max_val10_r0_val_f0),
    .max_val10_r1_val_f1(max_val10_r1_val_f1),
    .max_val11_r0_val_f0(max_val11_r0_val_f0),
    .max_val11_r1_val_f1(max_val11_r1_val_f1),
    .rel_mask0_val(rel_mask0),
    .rel_mask1_val(rel_mask1),
    .rel_mask2_val(rel_mask2),
    .rel_mask3_val(rel_mask3),
    .rel_mask4_val(rel_mask4),
    .rel_mask5_val(rel_mask5),
    .rel_mask6_val(rel_mask6),
    .rel_mask7_val(rel_mask7),
    .rel_mask8_val(rel_mask8),
    .rel_mask9_val(rel_mask9),
    .rel_mask10_val(rel_mask10),
    .rel_mask11_val(rel_mask11),
    .rel_mask12_val(rel_mask12),
    .rel_mask13_val(rel_mask13),
    .rel_mask14_val(rel_mask14),
    .rel_mask15_val(rel_mask15),
    .rel_mask16_val(rel_mask16),
    .rel_mask17_val(rel_mask17),
    .rel_mask18_val(rel_mask18),
    .rel_mask19_val(rel_mask19),
    .rel_mask20_val(rel_mask20),
    .rel_mask21_val(rel_mask21),
    .rel_mask22_val(rel_mask22),
    .rel_mask23_val(rel_mask23),
    .rel_mask24_val(rel_mask24),
    .rel_mask25_val(rel_mask25),
    .rel_mask26_val(rel_mask26),
    .rel_mask27_val(rel_mask27),
    .rel_mask28_val(rel_mask28),
    .rel_mask29_val(rel_mask29),
    .rel_mask30_val(rel_mask30),
    .rel_mask31_val(rel_mask31),
    .sel_delta_val(sel_delta),
    .trig_inv_val(trig_inv),
    .val_mask0_val(val_mask0),
    .val_mask1_val(val_mask1),
    .val_mask2_val(val_mask2),
    .val_mask3_val(val_mask3),
    .val_mask4_val(val_mask4),
    .val_mask5_val(val_mask5),
    .val_mask6_val(val_mask6),
    .val_mask7_val(val_mask7),
    .val_mask8_val(val_mask8),
    .val_mask9_val(val_mask9),
    .val_mask10_val(val_mask10),
    .val_mask11_val(val_mask11),
    .val_mask12_val(val_mask12),
    .val_mask13_val(val_mask13),
    .val_mask14_val(val_mask14),
    .val_mask15_val(val_mask15),
    .val_mask16_val(val_mask16),
    .val_mask17_val(val_mask17),
    .val_mask18_val(val_mask18),
    .val_mask19_val(val_mask19),
    .val_mask20_val(val_mask20),
    .val_mask21_val(val_mask21),
    .val_mask22_val(val_mask22),
    .val_mask23_val(val_mask23),
    .val_mask24_val(val_mask24),
    .val_mask25_val(val_mask25),
    .val_mask26_val(val_mask26),
    .val_mask27_val(val_mask27),
    .val_mask28_val(val_mask28),
    .val_mask29_val(val_mask29),
    .val_mask30_val(val_mask30),
    .val_mask31_val(val_mask31)
);

endmodule

//----------------------------------------------------------------------------
// counter
//----------------------------------------------------------------------------
module counter 
#(
    parameter WIDTH = 40)
(
    input clk,
    input clr,
    input en,
    input [WIDTH-1:0] max_val,
    input rst_n,
    output [WIDTH-1:0] cnt,
    output eq
);

reg [WIDTH-1:0] cnt;
reg eq;

always @(*) 
    eq <= cnt == max_val;

// clear and increment logic
// goes here

always @(posedge clk or negedge rst_n) 
    if (~rst_n) 
        cnt <= 0;
    else 
        if (clr) begin
            // clear has priority
            cnt <= 0;
        end
        else if (en) 
            cnt <= cnt + 1;

endmodule

//----------------------------------------------------------------------------
// dbg_cnt_numCnt12_width40_numTc32
//----------------------------------------------------------------------------
module dbg_cnt_numCnt12_width40_numTc32 
#(
    parameter CNT_W = 40,
    parameter NUM_CNT = 12)
(
    input clk,
    input [NUM_CNT-1:0] clr,
    input [NUM_CNT-1:0] en,
    input [CNT_W-1:0] max_val0,
    input [CNT_W-1:0] max_val1,
    input [CNT_W-1:0] max_val2,
    input [CNT_W-1:0] max_val3,
    input [CNT_W-1:0] max_val4,
    input [CNT_W-1:0] max_val5,
    input [CNT_W-1:0] max_val6,
    input [CNT_W-1:0] max_val7,
    input [CNT_W-1:0] max_val8,
    input [CNT_W-1:0] max_val9,
    input [CNT_W-1:0] max_val10,
    input [CNT_W-1:0] max_val11,
    input rst_n,
    output [CNT_W-1:0] cnt0,
    output [CNT_W-1:0] cnt1,
    output [CNT_W-1:0] cnt2,
    output [CNT_W-1:0] cnt3,
    output [CNT_W-1:0] cnt4,
    output [CNT_W-1:0] cnt5,
    output [CNT_W-1:0] cnt6,
    output [CNT_W-1:0] cnt7,
    output [CNT_W-1:0] cnt8,
    output [CNT_W-1:0] cnt9,
    output [CNT_W-1:0] cnt10,
    output [CNT_W-1:0] cnt11,
    output [NUM_CNT-1:0] eq
);



counter #(
    .WIDTH(CNT_W)
) counter_0 (
    .clk(clk),
    .clr(clr[0]),
    .en(en[0]),
    .max_val(max_val0),
    .rst_n(rst_n),
    .cnt(cnt0),
    .eq(eq[0])
);

counter #(
    .WIDTH(CNT_W)
) counter_1 (
    .clk(clk),
    .clr(clr[1]),
    .en(en[1]),
    .max_val(max_val1),
    .rst_n(rst_n),
    .cnt(cnt1),
    .eq(eq[1])
);

counter #(
    .WIDTH(CNT_W)
) counter_2 (
    .clk(clk),
    .clr(clr[2]),
    .en(en[2]),
    .max_val(max_val2),
    .rst_n(rst_n),
    .cnt(cnt2),
    .eq(eq[2])
);

counter #(
    .WIDTH(CNT_W)
) counter_3 (
    .clk(clk),
    .clr(clr[3]),
    .en(en[3]),
    .max_val(max_val3),
    .rst_n(rst_n),
    .cnt(cnt3),
    .eq(eq[3])
);

counter #(
    .WIDTH(CNT_W)
) counter_4 (
    .clk(clk),
    .clr(clr[4]),
    .en(en[4]),
    .max_val(max_val4),
    .rst_n(rst_n),
    .cnt(cnt4),
    .eq(eq[4])
);

counter #(
    .WIDTH(CNT_W)
) counter_5 (
    .clk(clk),
    .clr(clr[5]),
    .en(en[5]),
    .max_val(max_val5),
    .rst_n(rst_n),
    .cnt(cnt5),
    .eq(eq[5])
);

counter #(
    .WIDTH(CNT_W)
) counter_6 (
    .clk(clk),
    .clr(clr[6]),
    .en(en[6]),
    .max_val(max_val6),
    .rst_n(rst_n),
    .cnt(cnt6),
    .eq(eq[6])
);

counter #(
    .WIDTH(CNT_W)
) counter_7 (
    .clk(clk),
    .clr(clr[7]),
    .en(en[7]),
    .max_val(max_val7),
    .rst_n(rst_n),
    .cnt(cnt7),
    .eq(eq[7])
);

counter #(
    .WIDTH(CNT_W)
) counter_8 (
    .clk(clk),
    .clr(clr[8]),
    .en(en[8]),
    .max_val(max_val8),
    .rst_n(rst_n),
    .cnt(cnt8),
    .eq(eq[8])
);

counter #(
    .WIDTH(CNT_W)
) counter_9 (
    .clk(clk),
    .clr(clr[9]),
    .en(en[9]),
    .max_val(max_val9),
    .rst_n(rst_n),
    .cnt(cnt9),
    .eq(eq[9])
);

counter #(
    .WIDTH(CNT_W)
) counter_10 (
    .clk(clk),
    .clr(clr[10]),
    .en(en[10]),
    .max_val(max_val10),
    .rst_n(rst_n),
    .cnt(cnt10),
    .eq(eq[10])
);

counter #(
    .WIDTH(CNT_W)
) counter_11 (
    .clk(clk),
    .clr(clr[11]),
    .en(en[11]),
    .max_val(max_val11),
    .rst_n(rst_n),
    .cnt(cnt11),
    .eq(eq[11])
);

endmodule

//----------------------------------------------------------------------------
// debug_numCnt12_width40_numTc32
//----------------------------------------------------------------------------
module debug_numCnt12_width40_numTc32 
#(
    parameter CNT_W = 40,
    parameter IN_W = 20,
    parameter NUM_CNT = 12,
    parameter NUM_TC = 32)
(
    input [(NUM_TC >> 1) - 1:0] chain_tc,
    input clk,
    input [NUM_CNT-1:0] clr_sel_mode_any,
    input [NUM_TC-1:0] clr_tc_mask0,
    input [NUM_TC-1:0] clr_tc_mask1,
    input [NUM_TC-1:0] clr_tc_mask2,
    input [NUM_TC-1:0] clr_tc_mask3,
    input [NUM_TC-1:0] clr_tc_mask4,
    input [NUM_TC-1:0] clr_tc_mask5,
    input [NUM_TC-1:0] clr_tc_mask6,
    input [NUM_TC-1:0] clr_tc_mask7,
    input [NUM_TC-1:0] clr_tc_mask8,
    input [NUM_TC-1:0] clr_tc_mask9,
    input [NUM_TC-1:0] clr_tc_mask10,
    input [NUM_TC-1:0] clr_tc_mask11,
    input [IN_W-1:0] dbg_in,
    input [NUM_CNT-1:0] inc_sel_mode_any,
    input [NUM_TC-1:0] inc_tc_mask0,
    input [NUM_TC-1:0] inc_tc_mask1,
    input [NUM_TC-1:0] inc_tc_mask2,
    input [NUM_TC-1:0] inc_tc_mask3,
    input [NUM_TC-1:0] inc_tc_mask4,
    input [NUM_TC-1:0] inc_tc_mask5,
    input [NUM_TC-1:0] inc_tc_mask6,
    input [NUM_TC-1:0] inc_tc_mask7,
    input [NUM_TC-1:0] inc_tc_mask8,
    input [NUM_TC-1:0] inc_tc_mask9,
    input [NUM_TC-1:0] inc_tc_mask10,
    input [NUM_TC-1:0] inc_tc_mask11,
    input [CNT_W-1:0] max_val0,
    input [CNT_W-1:0] max_val1,
    input [CNT_W-1:0] max_val2,
    input [CNT_W-1:0] max_val3,
    input [CNT_W-1:0] max_val4,
    input [CNT_W-1:0] max_val5,
    input [CNT_W-1:0] max_val6,
    input [CNT_W-1:0] max_val7,
    input [CNT_W-1:0] max_val8,
    input [CNT_W-1:0] max_val9,
    input [CNT_W-1:0] max_val10,
    input [CNT_W-1:0] max_val11,
    input [IN_W + NUM_CNT - 1:0] rel_mask0,
    input [IN_W + NUM_CNT - 1:0] rel_mask1,
    input [IN_W + NUM_CNT - 1:0] rel_mask2,
    input [IN_W + NUM_CNT - 1:0] rel_mask3,
    input [IN_W + NUM_CNT - 1:0] rel_mask4,
    input [IN_W + NUM_CNT - 1:0] rel_mask5,
    input [IN_W + NUM_CNT - 1:0] rel_mask6,
    input [IN_W + NUM_CNT - 1:0] rel_mask7,
    input [IN_W + NUM_CNT - 1:0] rel_mask8,
    input [IN_W + NUM_CNT - 1:0] rel_mask9,
    input [IN_W + NUM_CNT - 1:0] rel_mask10,
    input [IN_W + NUM_CNT - 1:0] rel_mask11,
    input [IN_W + NUM_CNT - 1:0] rel_mask12,
    input [IN_W + NUM_CNT - 1:0] rel_mask13,
    input [IN_W + NUM_CNT - 1:0] rel_mask14,
    input [IN_W + NUM_CNT - 1:0] rel_mask15,
    input [IN_W + NUM_CNT - 1:0] rel_mask16,
    input [IN_W + NUM_CNT - 1:0] rel_mask17,
    input [IN_W + NUM_CNT - 1:0] rel_mask18,
    input [IN_W + NUM_CNT - 1:0] rel_mask19,
    input [IN_W + NUM_CNT - 1:0] rel_mask20,
    input [IN_W + NUM_CNT - 1:0] rel_mask21,
    input [IN_W + NUM_CNT - 1:0] rel_mask22,
    input [IN_W + NUM_CNT - 1:0] rel_mask23,
    input [IN_W + NUM_CNT - 1:0] rel_mask24,
    input [IN_W + NUM_CNT - 1:0] rel_mask25,
    input [IN_W + NUM_CNT - 1:0] rel_mask26,
    input [IN_W + NUM_CNT - 1:0] rel_mask27,
    input [IN_W + NUM_CNT - 1:0] rel_mask28,
    input [IN_W + NUM_CNT - 1:0] rel_mask29,
    input [IN_W + NUM_CNT - 1:0] rel_mask30,
    input [IN_W + NUM_CNT - 1:0] rel_mask31,
    input rst_n,
    input [NUM_TC-1:0] sel_delta,
    input [NUM_TC-1:0] trig_inv,
    input [IN_W + NUM_CNT - 1:0] val_mask0,
    input [IN_W + NUM_CNT - 1:0] val_mask1,
    input [IN_W + NUM_CNT - 1:0] val_mask2,
    input [IN_W + NUM_CNT - 1:0] val_mask3,
    input [IN_W + NUM_CNT - 1:0] val_mask4,
    input [IN_W + NUM_CNT - 1:0] val_mask5,
    input [IN_W + NUM_CNT - 1:0] val_mask6,
    input [IN_W + NUM_CNT - 1:0] val_mask7,
    input [IN_W + NUM_CNT - 1:0] val_mask8,
    input [IN_W + NUM_CNT - 1:0] val_mask9,
    input [IN_W + NUM_CNT - 1:0] val_mask10,
    input [IN_W + NUM_CNT - 1:0] val_mask11,
    input [IN_W + NUM_CNT - 1:0] val_mask12,
    input [IN_W + NUM_CNT - 1:0] val_mask13,
    input [IN_W + NUM_CNT - 1:0] val_mask14,
    input [IN_W + NUM_CNT - 1:0] val_mask15,
    input [IN_W + NUM_CNT - 1:0] val_mask16,
    input [IN_W + NUM_CNT - 1:0] val_mask17,
    input [IN_W + NUM_CNT - 1:0] val_mask18,
    input [IN_W + NUM_CNT - 1:0] val_mask19,
    input [IN_W + NUM_CNT - 1:0] val_mask20,
    input [IN_W + NUM_CNT - 1:0] val_mask21,
    input [IN_W + NUM_CNT - 1:0] val_mask22,
    input [IN_W + NUM_CNT - 1:0] val_mask23,
    input [IN_W + NUM_CNT - 1:0] val_mask24,
    input [IN_W + NUM_CNT - 1:0] val_mask25,
    input [IN_W + NUM_CNT - 1:0] val_mask26,
    input [IN_W + NUM_CNT - 1:0] val_mask27,
    input [IN_W + NUM_CNT - 1:0] val_mask28,
    input [IN_W + NUM_CNT - 1:0] val_mask29,
    input [IN_W + NUM_CNT - 1:0] val_mask30,
    input [IN_W + NUM_CNT - 1:0] val_mask31,
    output [CNT_W-1:0] cnt0,
    output [CNT_W-1:0] cnt1,
    output [CNT_W-1:0] cnt2,
    output [CNT_W-1:0] cnt3,
    output [CNT_W-1:0] cnt4,
    output [CNT_W-1:0] cnt5,
    output [CNT_W-1:0] cnt6,
    output [CNT_W-1:0] cnt7,
    output [CNT_W-1:0] cnt8,
    output [CNT_W-1:0] cnt9,
    output [CNT_W-1:0] cnt10,
    output [CNT_W-1:0] cnt11
);
wire [NUM_CNT-1:0] eq; // auto
reg [NUM_CNT-1:0] clr;
reg [IN_W + NUM_CNT - 1:0] dbg;
reg [IN_W + NUM_CNT - 1:0] dbg_delta;
reg [IN_W + NUM_CNT - 1:0] dbg_q;
reg [IN_W + NUM_CNT - 1:0] eff_dbg0;
reg [IN_W + NUM_CNT - 1:0] eff_dbg1;
reg [IN_W + NUM_CNT - 1:0] eff_dbg2;
reg [IN_W + NUM_CNT - 1:0] eff_dbg3;
reg [IN_W + NUM_CNT - 1:0] eff_dbg4;
reg [IN_W + NUM_CNT - 1:0] eff_dbg5;
reg [IN_W + NUM_CNT - 1:0] eff_dbg6;
reg [IN_W + NUM_CNT - 1:0] eff_dbg7;
reg [IN_W + NUM_CNT - 1:0] eff_dbg8;
reg [IN_W + NUM_CNT - 1:0] eff_dbg9;
reg [IN_W + NUM_CNT - 1:0] eff_dbg10;
reg [IN_W + NUM_CNT - 1:0] eff_dbg11;
reg [IN_W + NUM_CNT - 1:0] eff_dbg12;
reg [IN_W + NUM_CNT - 1:0] eff_dbg13;
reg [IN_W + NUM_CNT - 1:0] eff_dbg14;
reg [IN_W + NUM_CNT - 1:0] eff_dbg15;
reg [IN_W + NUM_CNT - 1:0] eff_dbg16;
reg [IN_W + NUM_CNT - 1:0] eff_dbg17;
reg [IN_W + NUM_CNT - 1:0] eff_dbg18;
reg [IN_W + NUM_CNT - 1:0] eff_dbg19;
reg [IN_W + NUM_CNT - 1:0] eff_dbg20;
reg [IN_W + NUM_CNT - 1:0] eff_dbg21;
reg [IN_W + NUM_CNT - 1:0] eff_dbg22;
reg [IN_W + NUM_CNT - 1:0] eff_dbg23;
reg [IN_W + NUM_CNT - 1:0] eff_dbg24;
reg [IN_W + NUM_CNT - 1:0] eff_dbg25;
reg [IN_W + NUM_CNT - 1:0] eff_dbg26;
reg [IN_W + NUM_CNT - 1:0] eff_dbg27;
reg [IN_W + NUM_CNT - 1:0] eff_dbg28;
reg [IN_W + NUM_CNT - 1:0] eff_dbg29;
reg [IN_W + NUM_CNT - 1:0] eff_dbg30;
reg [IN_W + NUM_CNT - 1:0] eff_dbg31;
reg [NUM_TC-1:0] eff_tc_bus;
reg [NUM_CNT-1:0] en;
reg [NUM_TC-1:0] tc_bus;

always @(posedge clk or negedge rst_n) 
    if (~rst_n) 
        dbg_q <= 0;
    else 
        dbg_q <= dbg;

always @(*) begin
    dbg <= {
        dbg_in,
        eq};
    dbg_delta <= dbg ^ dbg_q;
    // Generate raw trigger conditions
    eff_dbg0 <= sel_delta[0] ? dbg_delta : dbg;
    eff_dbg1 <= sel_delta[1] ? dbg_delta : dbg;
    eff_dbg2 <= sel_delta[2] ? dbg_delta : dbg;
    eff_dbg3 <= sel_delta[3] ? dbg_delta : dbg;
    eff_dbg4 <= sel_delta[4] ? dbg_delta : dbg;
    eff_dbg5 <= sel_delta[5] ? dbg_delta : dbg;
    eff_dbg6 <= sel_delta[6] ? dbg_delta : dbg;
    eff_dbg7 <= sel_delta[7] ? dbg_delta : dbg;
    eff_dbg8 <= sel_delta[8] ? dbg_delta : dbg;
    eff_dbg9 <= sel_delta[9] ? dbg_delta : dbg;
    eff_dbg10 <= sel_delta[10] ? dbg_delta : dbg;
    eff_dbg11 <= sel_delta[11] ? dbg_delta : dbg;
    eff_dbg12 <= sel_delta[12] ? dbg_delta : dbg;
    eff_dbg13 <= sel_delta[13] ? dbg_delta : dbg;
    eff_dbg14 <= sel_delta[14] ? dbg_delta : dbg;
    eff_dbg15 <= sel_delta[15] ? dbg_delta : dbg;
    eff_dbg16 <= sel_delta[16] ? dbg_delta : dbg;
    eff_dbg17 <= sel_delta[17] ? dbg_delta : dbg;
    eff_dbg18 <= sel_delta[18] ? dbg_delta : dbg;
    eff_dbg19 <= sel_delta[19] ? dbg_delta : dbg;
    eff_dbg20 <= sel_delta[20] ? dbg_delta : dbg;
    eff_dbg21 <= sel_delta[21] ? dbg_delta : dbg;
    eff_dbg22 <= sel_delta[22] ? dbg_delta : dbg;
    eff_dbg23 <= sel_delta[23] ? dbg_delta : dbg;
    eff_dbg24 <= sel_delta[24] ? dbg_delta : dbg;
    eff_dbg25 <= sel_delta[25] ? dbg_delta : dbg;
    eff_dbg26 <= sel_delta[26] ? dbg_delta : dbg;
    eff_dbg27 <= sel_delta[27] ? dbg_delta : dbg;
    eff_dbg28 <= sel_delta[28] ? dbg_delta : dbg;
    eff_dbg29 <= sel_delta[29] ? dbg_delta : dbg;
    eff_dbg30 <= sel_delta[30] ? dbg_delta : dbg;
    eff_dbg31 <= sel_delta[31] ? dbg_delta : dbg;
    tc_bus <= {
        trig_inv[31] ^ ~|((eff_dbg31 ^ val_mask31) & rel_mask31),
        trig_inv[30] ^ ~|((eff_dbg30 ^ val_mask30) & rel_mask30),
        trig_inv[29] ^ ~|((eff_dbg29 ^ val_mask29) & rel_mask29),
        trig_inv[28] ^ ~|((eff_dbg28 ^ val_mask28) & rel_mask28),
        trig_inv[27] ^ ~|((eff_dbg27 ^ val_mask27) & rel_mask27),
        trig_inv[26] ^ ~|((eff_dbg26 ^ val_mask26) & rel_mask26),
        trig_inv[25] ^ ~|((eff_dbg25 ^ val_mask25) & rel_mask25),
        trig_inv[24] ^ ~|((eff_dbg24 ^ val_mask24) & rel_mask24),
        trig_inv[23] ^ ~|((eff_dbg23 ^ val_mask23) & rel_mask23),
        trig_inv[22] ^ ~|((eff_dbg22 ^ val_mask22) & rel_mask22),
        trig_inv[21] ^ ~|((eff_dbg21 ^ val_mask21) & rel_mask21),
        trig_inv[20] ^ ~|((eff_dbg20 ^ val_mask20) & rel_mask20),
        trig_inv[19] ^ ~|((eff_dbg19 ^ val_mask19) & rel_mask19),
        trig_inv[18] ^ ~|((eff_dbg18 ^ val_mask18) & rel_mask18),
        trig_inv[17] ^ ~|((eff_dbg17 ^ val_mask17) & rel_mask17),
        trig_inv[16] ^ ~|((eff_dbg16 ^ val_mask16) & rel_mask16),
        trig_inv[15] ^ ~|((eff_dbg15 ^ val_mask15) & rel_mask15),
        trig_inv[14] ^ ~|((eff_dbg14 ^ val_mask14) & rel_mask14),
        trig_inv[13] ^ ~|((eff_dbg13 ^ val_mask13) & rel_mask13),
        trig_inv[12] ^ ~|((eff_dbg12 ^ val_mask12) & rel_mask12),
        trig_inv[11] ^ ~|((eff_dbg11 ^ val_mask11) & rel_mask11),
        trig_inv[10] ^ ~|((eff_dbg10 ^ val_mask10) & rel_mask10),
        trig_inv[9] ^ ~|((eff_dbg9 ^ val_mask9) & rel_mask9),
        trig_inv[8] ^ ~|((eff_dbg8 ^ val_mask8) & rel_mask8),
        trig_inv[7] ^ ~|((eff_dbg7 ^ val_mask7) & rel_mask7),
        trig_inv[6] ^ ~|((eff_dbg6 ^ val_mask6) & rel_mask6),
        trig_inv[5] ^ ~|((eff_dbg5 ^ val_mask5) & rel_mask5),
        trig_inv[4] ^ ~|((eff_dbg4 ^ val_mask4) & rel_mask4),
        trig_inv[3] ^ ~|((eff_dbg3 ^ val_mask3) & rel_mask3),
        trig_inv[2] ^ ~|((eff_dbg2 ^ val_mask2) & rel_mask2),
        trig_inv[1] ^ ~|((eff_dbg1 ^ val_mask1) & rel_mask1),
        trig_inv[0] ^ ~|((eff_dbg0 ^ val_mask0) & rel_mask0)};
    // Generate effective triggers
    eff_tc_bus[0] <= tc_bus[0];
    eff_tc_bus[1] <= tc_bus[1] & (chain_tc[0] ? tc_bus[0] : 1);
    eff_tc_bus[2] <= tc_bus[2];
    eff_tc_bus[3] <= tc_bus[3] & (chain_tc[1] ? tc_bus[2] : 1);
    eff_tc_bus[4] <= tc_bus[4];
    eff_tc_bus[5] <= tc_bus[5] & (chain_tc[2] ? tc_bus[4] : 1);
    eff_tc_bus[6] <= tc_bus[6];
    eff_tc_bus[7] <= tc_bus[7] & (chain_tc[3] ? tc_bus[6] : 1);
    eff_tc_bus[8] <= tc_bus[8];
    eff_tc_bus[9] <= tc_bus[9] & (chain_tc[4] ? tc_bus[8] : 1);
    eff_tc_bus[10] <= tc_bus[10];
    eff_tc_bus[11] <= tc_bus[11] & (chain_tc[5] ? tc_bus[10] : 1);
    eff_tc_bus[12] <= tc_bus[12];
    eff_tc_bus[13] <= tc_bus[13] & (chain_tc[6] ? tc_bus[12] : 1);
    eff_tc_bus[14] <= tc_bus[14];
    eff_tc_bus[15] <= tc_bus[15] & (chain_tc[7] ? tc_bus[14] : 1);
    eff_tc_bus[16] <= tc_bus[16];
    eff_tc_bus[17] <= tc_bus[17] & (chain_tc[8] ? tc_bus[16] : 1);
    eff_tc_bus[18] <= tc_bus[18];
    eff_tc_bus[19] <= tc_bus[19] & (chain_tc[9] ? tc_bus[18] : 1);
    eff_tc_bus[20] <= tc_bus[20];
    eff_tc_bus[21] <= tc_bus[21] & (chain_tc[10] ? tc_bus[20] : 1);
    eff_tc_bus[22] <= tc_bus[22];
    eff_tc_bus[23] <= tc_bus[23] & (chain_tc[11] ? tc_bus[22] : 1);
    eff_tc_bus[24] <= tc_bus[24];
    eff_tc_bus[25] <= tc_bus[25] & (chain_tc[12] ? tc_bus[24] : 1);
    eff_tc_bus[26] <= tc_bus[26];
    eff_tc_bus[27] <= tc_bus[27] & (chain_tc[13] ? tc_bus[26] : 1);
    eff_tc_bus[28] <= tc_bus[28];
    eff_tc_bus[29] <= tc_bus[29] & (chain_tc[14] ? tc_bus[28] : 1);
    eff_tc_bus[30] <= tc_bus[30];
    eff_tc_bus[31] <= tc_bus[31] & (chain_tc[15] ? tc_bus[30] : 1);
    // Generate counter increment enables
    en[0] <= inc_sel_mode_any ? |(eff_tc_bus & inc_tc_mask0) : &(eff_tc_bus & ~inc_tc_mask0);
    en[1] <= inc_sel_mode_any ? |(eff_tc_bus & inc_tc_mask1) : &(eff_tc_bus & ~inc_tc_mask1);
    en[2] <= inc_sel_mode_any ? |(eff_tc_bus & inc_tc_mask2) : &(eff_tc_bus & ~inc_tc_mask2);
    en[3] <= inc_sel_mode_any ? |(eff_tc_bus & inc_tc_mask3) : &(eff_tc_bus & ~inc_tc_mask3);
    en[4] <= inc_sel_mode_any ? |(eff_tc_bus & inc_tc_mask4) : &(eff_tc_bus & ~inc_tc_mask4);
    en[5] <= inc_sel_mode_any ? |(eff_tc_bus & inc_tc_mask5) : &(eff_tc_bus & ~inc_tc_mask5);
    en[6] <= inc_sel_mode_any ? |(eff_tc_bus & inc_tc_mask6) : &(eff_tc_bus & ~inc_tc_mask6);
    en[7] <= inc_sel_mode_any ? |(eff_tc_bus & inc_tc_mask7) : &(eff_tc_bus & ~inc_tc_mask7);
    en[8] <= inc_sel_mode_any ? |(eff_tc_bus & inc_tc_mask8) : &(eff_tc_bus & ~inc_tc_mask8);
    en[9] <= inc_sel_mode_any ? |(eff_tc_bus & inc_tc_mask9) : &(eff_tc_bus & ~inc_tc_mask9);
    en[10] <= inc_sel_mode_any ? |(eff_tc_bus & inc_tc_mask10) : &(eff_tc_bus & ~inc_tc_mask10);
    en[11] <= inc_sel_mode_any ? |(eff_tc_bus & inc_tc_mask11) : &(eff_tc_bus & ~inc_tc_mask11);
    // Generate counter clear enables
    clr[0] <= clr_sel_mode_any ? |(eff_tc_bus & clr_tc_mask0) : &(eff_tc_bus & ~clr_tc_mask0);
    clr[1] <= clr_sel_mode_any ? |(eff_tc_bus & clr_tc_mask1) : &(eff_tc_bus & ~clr_tc_mask1);
    clr[2] <= clr_sel_mode_any ? |(eff_tc_bus & clr_tc_mask2) : &(eff_tc_bus & ~clr_tc_mask2);
    clr[3] <= clr_sel_mode_any ? |(eff_tc_bus & clr_tc_mask3) : &(eff_tc_bus & ~clr_tc_mask3);
    clr[4] <= clr_sel_mode_any ? |(eff_tc_bus & clr_tc_mask4) : &(eff_tc_bus & ~clr_tc_mask4);
    clr[5] <= clr_sel_mode_any ? |(eff_tc_bus & clr_tc_mask5) : &(eff_tc_bus & ~clr_tc_mask5);
    clr[6] <= clr_sel_mode_any ? |(eff_tc_bus & clr_tc_mask6) : &(eff_tc_bus & ~clr_tc_mask6);
    clr[7] <= clr_sel_mode_any ? |(eff_tc_bus & clr_tc_mask7) : &(eff_tc_bus & ~clr_tc_mask7);
    clr[8] <= clr_sel_mode_any ? |(eff_tc_bus & clr_tc_mask8) : &(eff_tc_bus & ~clr_tc_mask8);
    clr[9] <= clr_sel_mode_any ? |(eff_tc_bus & clr_tc_mask9) : &(eff_tc_bus & ~clr_tc_mask9);
    clr[10] <= clr_sel_mode_any ? |(eff_tc_bus & clr_tc_mask10) : &(eff_tc_bus & ~clr_tc_mask10);
    clr[11] <= clr_sel_mode_any ? |(eff_tc_bus & clr_tc_mask11) : &(eff_tc_bus & ~clr_tc_mask11);
end

dbg_cnt_numCnt12_width40_numTc32  dbg_cnt_numCnt12_width40_numTc32_0 (
    .clk(clk),
    .clr(clr),
    .en(en),
    .max_val0(max_val0),
    .max_val1(max_val1),
    .max_val2(max_val2),
    .max_val3(max_val3),
    .max_val4(max_val4),
    .max_val5(max_val5),
    .max_val6(max_val6),
    .max_val7(max_val7),
    .max_val8(max_val8),
    .max_val9(max_val9),
    .max_val10(max_val10),
    .max_val11(max_val11),
    .rst_n(rst_n),
    .cnt0(cnt0),
    .cnt1(cnt1),
    .cnt2(cnt2),
    .cnt3(cnt3),
    .cnt4(cnt4),
    .cnt5(cnt5),
    .cnt6(cnt6),
    .cnt7(cnt7),
    .cnt8(cnt8),
    .cnt9(cnt9),
    .cnt10(cnt10),
    .cnt11(cnt11),
    .eq(eq)
);

endmodule

//----------------------------------------------------------------------------
// debug_apb
//----------------------------------------------------------------------------
module debug_apb 
#(
    parameter CNT_W = 40,
    parameter IN_W = 20,
    parameter NUM_CNT = 12,
    parameter NUM_TC = 32)
(
    input [31:0] PADDR,
    input PENABLE,
    input PSEL,
    input [31:0] PWDATA,
    input PWRITE,
    input clk,
    input [39:0] cnt0_val,
    input [39:0] cnt10_val,
    input [39:0] cnt11_val,
    input [39:0] cnt1_val,
    input [39:0] cnt2_val,
    input [39:0] cnt3_val,
    input [39:0] cnt4_val,
    input [39:0] cnt5_val,
    input [39:0] cnt6_val,
    input [39:0] cnt7_val,
    input [39:0] cnt8_val,
    input [39:0] cnt9_val,
    input [IN_W-1:0] dbg_in,
    input [CNT_W-1:0] max_val0,
    input [CNT_W-1:0] max_val1,
    input [CNT_W-1:0] max_val2,
    input [CNT_W-1:0] max_val3,
    input [CNT_W-1:0] max_val4,
    input [CNT_W-1:0] max_val5,
    input [CNT_W-1:0] max_val6,
    input [CNT_W-1:0] max_val7,
    input [CNT_W-1:0] max_val8,
    input [CNT_W-1:0] max_val9,
    input [CNT_W-1:0] max_val10,
    input [CNT_W-1:0] max_val11,
    input rst_n,
    output [31:0] PRDATA,
    output PREADY,
    output PSLVERR,
    output [CNT_W-1:0] cnt0,
    output [CNT_W-1:0] cnt1,
    output [CNT_W-1:0] cnt2,
    output [CNT_W-1:0] cnt3,
    output [CNT_W-1:0] cnt4,
    output [CNT_W-1:0] cnt5,
    output [CNT_W-1:0] cnt6,
    output [CNT_W-1:0] cnt7,
    output [CNT_W-1:0] cnt8,
    output [CNT_W-1:0] cnt9,
    output [CNT_W-1:0] cnt10,
    output [CNT_W-1:0] cnt11,
    output [39:0] max_val0_val,
    output [39:0] max_val10_val,
    output [39:0] max_val11_val,
    output [39:0] max_val1_val,
    output [39:0] max_val2_val,
    output [39:0] max_val3_val,
    output [39:0] max_val4_val,
    output [39:0] max_val5_val,
    output [39:0] max_val6_val,
    output [39:0] max_val7_val,
    output [39:0] max_val8_val,
    output [39:0] max_val9_val
);
wire [15:0] chain_tc; // auto
wire [11:0] clr_sel_mode_any; // auto
wire [31:0] clr_tc_mask0; // auto
wire [31:0] clr_tc_mask1; // auto
wire [31:0] clr_tc_mask2; // auto
wire [31:0] clr_tc_mask3; // auto
wire [31:0] clr_tc_mask4; // auto
wire [31:0] clr_tc_mask5; // auto
wire [31:0] clr_tc_mask6; // auto
wire [31:0] clr_tc_mask7; // auto
wire [31:0] clr_tc_mask8; // auto
wire [31:0] clr_tc_mask9; // auto
wire [31:0] clr_tc_mask10; // auto
wire [31:0] clr_tc_mask11; // auto
wire [11:0] inc_sel_mode_any; // auto
wire [31:0] inc_tc_mask0; // auto
wire [31:0] inc_tc_mask1; // auto
wire [31:0] inc_tc_mask2; // auto
wire [31:0] inc_tc_mask3; // auto
wire [31:0] inc_tc_mask4; // auto
wire [31:0] inc_tc_mask5; // auto
wire [31:0] inc_tc_mask6; // auto
wire [31:0] inc_tc_mask7; // auto
wire [31:0] inc_tc_mask8; // auto
wire [31:0] inc_tc_mask9; // auto
wire [31:0] inc_tc_mask10; // auto
wire [31:0] inc_tc_mask11; // auto
wire [31:0] rel_mask0; // auto
wire [31:0] rel_mask1; // auto
wire [31:0] rel_mask2; // auto
wire [31:0] rel_mask3; // auto
wire [31:0] rel_mask4; // auto
wire [31:0] rel_mask5; // auto
wire [31:0] rel_mask6; // auto
wire [31:0] rel_mask7; // auto
wire [31:0] rel_mask8; // auto
wire [31:0] rel_mask9; // auto
wire [31:0] rel_mask10; // auto
wire [31:0] rel_mask11; // auto
wire [31:0] rel_mask12; // auto
wire [31:0] rel_mask13; // auto
wire [31:0] rel_mask14; // auto
wire [31:0] rel_mask15; // auto
wire [31:0] rel_mask16; // auto
wire [31:0] rel_mask17; // auto
wire [31:0] rel_mask18; // auto
wire [31:0] rel_mask19; // auto
wire [31:0] rel_mask20; // auto
wire [31:0] rel_mask21; // auto
wire [31:0] rel_mask22; // auto
wire [31:0] rel_mask23; // auto
wire [31:0] rel_mask24; // auto
wire [31:0] rel_mask25; // auto
wire [31:0] rel_mask26; // auto
wire [31:0] rel_mask27; // auto
wire [31:0] rel_mask28; // auto
wire [31:0] rel_mask29; // auto
wire [31:0] rel_mask30; // auto
wire [31:0] rel_mask31; // auto
wire [31:0] sel_delta; // auto
wire [31:0] trig_inv; // auto
wire [31:0] val_mask0; // auto
wire [31:0] val_mask1; // auto
wire [31:0] val_mask2; // auto
wire [31:0] val_mask3; // auto
wire [31:0] val_mask4; // auto
wire [31:0] val_mask5; // auto
wire [31:0] val_mask6; // auto
wire [31:0] val_mask7; // auto
wire [31:0] val_mask8; // auto
wire [31:0] val_mask9; // auto
wire [31:0] val_mask10; // auto
wire [31:0] val_mask11; // auto
wire [31:0] val_mask12; // auto
wire [31:0] val_mask13; // auto
wire [31:0] val_mask14; // auto
wire [31:0] val_mask15; // auto
wire [31:0] val_mask16; // auto
wire [31:0] val_mask17; // auto
wire [31:0] val_mask18; // auto
wire [31:0] val_mask19; // auto
wire [31:0] val_mask20; // auto
wire [31:0] val_mask21; // auto
wire [31:0] val_mask22; // auto
wire [31:0] val_mask23; // auto
wire [31:0] val_mask24; // auto
wire [31:0] val_mask25; // auto
wire [31:0] val_mask26; // auto
wire [31:0] val_mask27; // auto
wire [31:0] val_mask28; // auto
wire [31:0] val_mask29; // auto
wire [31:0] val_mask30; // auto
wire [31:0] val_mask31; // auto


debug_apb_csr_wrap  debug_apb_csr_wrap_0 (
    .PADDR(PADDR),
    .PENABLE(PENABLE),
    .PSEL(PSEL),
    .PWDATA(PWDATA),
    .PWRITE(PWRITE),
    .clk(clk),
    .cnt0_val(cnt0_val),
    .cnt10_val(cnt10_val),
    .cnt11_val(cnt11_val),
    .cnt1_val(cnt1_val),
    .cnt2_val(cnt2_val),
    .cnt3_val(cnt3_val),
    .cnt4_val(cnt4_val),
    .cnt5_val(cnt5_val),
    .cnt6_val(cnt6_val),
    .cnt7_val(cnt7_val),
    .cnt8_val(cnt8_val),
    .cnt9_val(cnt9_val),
    .rst_n(rst_n),
    .PRDATA(PRDATA),
    .PREADY(PREADY),
    .PSLVERR(PSLVERR),
    .chain_tc(chain_tc),
    .clr_sel_mode_any(clr_sel_mode_any),
    .clr_tc_mask0(clr_tc_mask0),
    .clr_tc_mask1(clr_tc_mask1),
    .clr_tc_mask2(clr_tc_mask2),
    .clr_tc_mask3(clr_tc_mask3),
    .clr_tc_mask4(clr_tc_mask4),
    .clr_tc_mask5(clr_tc_mask5),
    .clr_tc_mask6(clr_tc_mask6),
    .clr_tc_mask7(clr_tc_mask7),
    .clr_tc_mask8(clr_tc_mask8),
    .clr_tc_mask9(clr_tc_mask9),
    .clr_tc_mask10(clr_tc_mask10),
    .clr_tc_mask11(clr_tc_mask11),
    .inc_sel_mode_any(inc_sel_mode_any),
    .inc_tc_mask0(inc_tc_mask0),
    .inc_tc_mask1(inc_tc_mask1),
    .inc_tc_mask2(inc_tc_mask2),
    .inc_tc_mask3(inc_tc_mask3),
    .inc_tc_mask4(inc_tc_mask4),
    .inc_tc_mask5(inc_tc_mask5),
    .inc_tc_mask6(inc_tc_mask6),
    .inc_tc_mask7(inc_tc_mask7),
    .inc_tc_mask8(inc_tc_mask8),
    .inc_tc_mask9(inc_tc_mask9),
    .inc_tc_mask10(inc_tc_mask10),
    .inc_tc_mask11(inc_tc_mask11),
    .max_val0_val(max_val0_val),
    .max_val10_val(max_val10_val),
    .max_val11_val(max_val11_val),
    .max_val1_val(max_val1_val),
    .max_val2_val(max_val2_val),
    .max_val3_val(max_val3_val),
    .max_val4_val(max_val4_val),
    .max_val5_val(max_val5_val),
    .max_val6_val(max_val6_val),
    .max_val7_val(max_val7_val),
    .max_val8_val(max_val8_val),
    .max_val9_val(max_val9_val),
    .rel_mask0(rel_mask0),
    .rel_mask1(rel_mask1),
    .rel_mask2(rel_mask2),
    .rel_mask3(rel_mask3),
    .rel_mask4(rel_mask4),
    .rel_mask5(rel_mask5),
    .rel_mask6(rel_mask6),
    .rel_mask7(rel_mask7),
    .rel_mask8(rel_mask8),
    .rel_mask9(rel_mask9),
    .rel_mask10(rel_mask10),
    .rel_mask11(rel_mask11),
    .rel_mask12(rel_mask12),
    .rel_mask13(rel_mask13),
    .rel_mask14(rel_mask14),
    .rel_mask15(rel_mask15),
    .rel_mask16(rel_mask16),
    .rel_mask17(rel_mask17),
    .rel_mask18(rel_mask18),
    .rel_mask19(rel_mask19),
    .rel_mask20(rel_mask20),
    .rel_mask21(rel_mask21),
    .rel_mask22(rel_mask22),
    .rel_mask23(rel_mask23),
    .rel_mask24(rel_mask24),
    .rel_mask25(rel_mask25),
    .rel_mask26(rel_mask26),
    .rel_mask27(rel_mask27),
    .rel_mask28(rel_mask28),
    .rel_mask29(rel_mask29),
    .rel_mask30(rel_mask30),
    .rel_mask31(rel_mask31),
    .sel_delta(sel_delta),
    .trig_inv(trig_inv),
    .val_mask0(val_mask0),
    .val_mask1(val_mask1),
    .val_mask2(val_mask2),
    .val_mask3(val_mask3),
    .val_mask4(val_mask4),
    .val_mask5(val_mask5),
    .val_mask6(val_mask6),
    .val_mask7(val_mask7),
    .val_mask8(val_mask8),
    .val_mask9(val_mask9),
    .val_mask10(val_mask10),
    .val_mask11(val_mask11),
    .val_mask12(val_mask12),
    .val_mask13(val_mask13),
    .val_mask14(val_mask14),
    .val_mask15(val_mask15),
    .val_mask16(val_mask16),
    .val_mask17(val_mask17),
    .val_mask18(val_mask18),
    .val_mask19(val_mask19),
    .val_mask20(val_mask20),
    .val_mask21(val_mask21),
    .val_mask22(val_mask22),
    .val_mask23(val_mask23),
    .val_mask24(val_mask24),
    .val_mask25(val_mask25),
    .val_mask26(val_mask26),
    .val_mask27(val_mask27),
    .val_mask28(val_mask28),
    .val_mask29(val_mask29),
    .val_mask30(val_mask30),
    .val_mask31(val_mask31)
);

debug_numCnt12_width40_numTc32  debug_numCnt12_width40_numTc32_0 (
    .chain_tc(chain_tc),
    .clk(clk),
    .clr_sel_mode_any(clr_sel_mode_any),
    .clr_tc_mask0(clr_tc_mask0),
    .clr_tc_mask1(clr_tc_mask1),
    .clr_tc_mask2(clr_tc_mask2),
    .clr_tc_mask3(clr_tc_mask3),
    .clr_tc_mask4(clr_tc_mask4),
    .clr_tc_mask5(clr_tc_mask5),
    .clr_tc_mask6(clr_tc_mask6),
    .clr_tc_mask7(clr_tc_mask7),
    .clr_tc_mask8(clr_tc_mask8),
    .clr_tc_mask9(clr_tc_mask9),
    .clr_tc_mask10(clr_tc_mask10),
    .clr_tc_mask11(clr_tc_mask11),
    .dbg_in(dbg_in),
    .inc_sel_mode_any(inc_sel_mode_any),
    .inc_tc_mask0(inc_tc_mask0),
    .inc_tc_mask1(inc_tc_mask1),
    .inc_tc_mask2(inc_tc_mask2),
    .inc_tc_mask3(inc_tc_mask3),
    .inc_tc_mask4(inc_tc_mask4),
    .inc_tc_mask5(inc_tc_mask5),
    .inc_tc_mask6(inc_tc_mask6),
    .inc_tc_mask7(inc_tc_mask7),
    .inc_tc_mask8(inc_tc_mask8),
    .inc_tc_mask9(inc_tc_mask9),
    .inc_tc_mask10(inc_tc_mask10),
    .inc_tc_mask11(inc_tc_mask11),
    .max_val0(max_val0),
    .max_val1(max_val1),
    .max_val2(max_val2),
    .max_val3(max_val3),
    .max_val4(max_val4),
    .max_val5(max_val5),
    .max_val6(max_val6),
    .max_val7(max_val7),
    .max_val8(max_val8),
    .max_val9(max_val9),
    .max_val10(max_val10),
    .max_val11(max_val11),
    .rel_mask0(rel_mask0),
    .rel_mask1(rel_mask1),
    .rel_mask2(rel_mask2),
    .rel_mask3(rel_mask3),
    .rel_mask4(rel_mask4),
    .rel_mask5(rel_mask5),
    .rel_mask6(rel_mask6),
    .rel_mask7(rel_mask7),
    .rel_mask8(rel_mask8),
    .rel_mask9(rel_mask9),
    .rel_mask10(rel_mask10),
    .rel_mask11(rel_mask11),
    .rel_mask12(rel_mask12),
    .rel_mask13(rel_mask13),
    .rel_mask14(rel_mask14),
    .rel_mask15(rel_mask15),
    .rel_mask16(rel_mask16),
    .rel_mask17(rel_mask17),
    .rel_mask18(rel_mask18),
    .rel_mask19(rel_mask19),
    .rel_mask20(rel_mask20),
    .rel_mask21(rel_mask21),
    .rel_mask22(rel_mask22),
    .rel_mask23(rel_mask23),
    .rel_mask24(rel_mask24),
    .rel_mask25(rel_mask25),
    .rel_mask26(rel_mask26),
    .rel_mask27(rel_mask27),
    .rel_mask28(rel_mask28),
    .rel_mask29(rel_mask29),
    .rel_mask30(rel_mask30),
    .rel_mask31(rel_mask31),
    .rst_n(rst_n),
    .sel_delta(sel_delta),
    .trig_inv(trig_inv),
    .val_mask0(val_mask0),
    .val_mask1(val_mask1),
    .val_mask2(val_mask2),
    .val_mask3(val_mask3),
    .val_mask4(val_mask4),
    .val_mask5(val_mask5),
    .val_mask6(val_mask6),
    .val_mask7(val_mask7),
    .val_mask8(val_mask8),
    .val_mask9(val_mask9),
    .val_mask10(val_mask10),
    .val_mask11(val_mask11),
    .val_mask12(val_mask12),
    .val_mask13(val_mask13),
    .val_mask14(val_mask14),
    .val_mask15(val_mask15),
    .val_mask16(val_mask16),
    .val_mask17(val_mask17),
    .val_mask18(val_mask18),
    .val_mask19(val_mask19),
    .val_mask20(val_mask20),
    .val_mask21(val_mask21),
    .val_mask22(val_mask22),
    .val_mask23(val_mask23),
    .val_mask24(val_mask24),
    .val_mask25(val_mask25),
    .val_mask26(val_mask26),
    .val_mask27(val_mask27),
    .val_mask28(val_mask28),
    .val_mask29(val_mask29),
    .val_mask30(val_mask30),
    .val_mask31(val_mask31),
    .cnt0(cnt0),
    .cnt1(cnt1),
    .cnt2(cnt2),
    .cnt3(cnt3),
    .cnt4(cnt4),
    .cnt5(cnt5),
    .cnt6(cnt6),
    .cnt7(cnt7),
    .cnt8(cnt8),
    .cnt9(cnt9),
    .cnt10(cnt10),
    .cnt11(cnt11)
);

endmodule

