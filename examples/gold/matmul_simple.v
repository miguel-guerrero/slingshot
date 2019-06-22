//----------------------------------------------------------------------------
// matmul
//----------------------------------------------------------------------------
module matmul 
#(
    parameter DIM_BITS = 16,
    parameter MEM_AW = 16,
    parameter MEM_DW = 32,
    parameter PREC = 16)
(
    input [MEM_AW-1:0] aBASE,
    input [DIM_BITS-1:0] aCOLS,
    input [DIM_BITS-1:0] aROWS,
    input [DIM_BITS-1:0] aSTRIDE,
    input [MEM_AW-1:0] bBASE,
    input [DIM_BITS-1:0] bCOLS,
    input [DIM_BITS-1:0] bSTRIDE,
    input [MEM_AW-1:0] cBASE,
    input [DIM_BITS-1:0] cSTRIDE,
    input clk,
    input go,
    input [MEM_DW-1:0] mem_rdata,
    input rst_n,
    output reg [MEM_AW-1:0] mem_addr,
    output reg mem_req,
    output reg [MEM_DW-1:0] mem_wdata,
    output reg mem_write,
    output reg ret
);

// types
localparam SM_MATMUL_FSM_S0=0;
localparam SM_MATMUL_FSM_S1=1;
localparam SM_MATMUL_FSM_S2=2;
localparam SM_MATMUL_FSM_S3=3;
localparam SM_MATMUL_FSM_S4=4;
localparam SM_MATMUL_FSM_S5=5;
localparam SM_MATMUL_FSM_S6=6;
localparam SM_MATMUL_FSM_S7=7;
localparam SM_MATMUL_FSM_S8=8;
localparam SM_MATMUL_FSM_S9=9;
localparam SM_MATMUL_FSM_S10=10;
localparam SM_MATMUL_FSM_S11=11;

reg [PREC-1:0] a;
reg [MEM_AW-1:0] a_i0;
reg [MEM_AW-1:0] a_ik;
reg [MEM_DW-1:0] acc;
reg [MEM_AW-1:0] b_0j;
reg [MEM_AW-1:0] b_kj;
reg [MEM_AW-1:0] c_i0;
reg [MEM_AW-1:0] c_ij;
reg [DIM_BITS-1:0] i;
reg [DIM_BITS-1:0] j;
reg [DIM_BITS-1:0] k;
reg [3:0] matmul_fsm_state;

always @(posedge clk or negedge rst_n) begin
    if (~rst_n) begin
        a <= 0;
        a_i0 <= 0;
        a_ik <= 0;
        acc <= 0;
        b_0j <= 0;
        b_kj <= 0;
        c_i0 <= 0;
        c_ij <= 0;
        i <= 0;
        j <= 0;
        k <= 0;
        matmul_fsm_state <= SM_MATMUL_FSM_S0;
        mem_addr <= 0;
        mem_req <= 0;
        mem_wdata <= 0;
        mem_write <= 0;
        ret <= 0;
    end
    else begin : matmul_fsm_clocked
        case (matmul_fsm_state)
            SM_MATMUL_FSM_S0 : begin
                ret <= 0;
                matmul_fsm_state <= SM_MATMUL_FSM_S1;
            end
            SM_MATMUL_FSM_S1 : begin
                if (~go) begin
                    // stay
                end
                else begin
                    a_i0 <= aBASE;
                    c_i0 <= cBASE;
                    i <= 0;
                    matmul_fsm_state <= SM_MATMUL_FSM_S2;
                end
            end
            SM_MATMUL_FSM_S2 : begin
                if (aROWS != i) begin
                    b_0j <= bBASE;
                    c_ij <= c_i0;
                    j <= 0;
                    matmul_fsm_state <= SM_MATMUL_FSM_S3;
                end
                else begin
                    ret <= 1;
                    matmul_fsm_state <= SM_MATMUL_FSM_S11;
                end
            end
            SM_MATMUL_FSM_S3 : begin
                if (bCOLS != j) begin
                    a_ik <= a_i0;
                    b_kj <= b_0j;
                    acc <= 0;
                    k <= 0;
                    matmul_fsm_state <= SM_MATMUL_FSM_S4;
                end
                else begin
                    a_i0 <= a_i0 + aSTRIDE;
                    c_i0 <= c_i0 + cSTRIDE;
                    i <= i + 1;
                    matmul_fsm_state <= SM_MATMUL_FSM_S2;
                end
            end
            SM_MATMUL_FSM_S4 : begin
                mem_addr <= a_ik;
                mem_write <= 0;
                mem_req <= 1;
                a_ik <= a_ik + 1;
                matmul_fsm_state <= SM_MATMUL_FSM_S5;
            end
            SM_MATMUL_FSM_S5 : begin
                mem_addr <= b_kj;
                mem_write <= 0;
                mem_req <= 1;
                b_kj <= b_kj + bSTRIDE;
                if (aCOLS != k) begin
                    matmul_fsm_state <= SM_MATMUL_FSM_S6;
                end
                else begin
                    mem_req <= 0;
                    matmul_fsm_state <= SM_MATMUL_FSM_S9;
                end
            end
            SM_MATMUL_FSM_S6 : begin
                k <= k + 1;
                matmul_fsm_state <= SM_MATMUL_FSM_S7;
            end
            SM_MATMUL_FSM_S7 : begin
                mem_addr <= a_ik;
                mem_write <= 0;
                mem_req <= 1;
                a_ik <= a_ik + 1;
                a <= mem_rdata[PREC-1:0];
                matmul_fsm_state <= SM_MATMUL_FSM_S8;
            end
            SM_MATMUL_FSM_S8 : begin
                mem_addr <= b_kj;
                mem_write <= 0;
                mem_req <= 1;
                b_kj <= b_kj + bSTRIDE;
                acc <= acc + a[PREC-1:0] * mem_rdata[PREC-1:0];
                if (aCOLS != k) begin
                    matmul_fsm_state <= SM_MATMUL_FSM_S6;
                end
                else begin
                    mem_req <= 0;
                    matmul_fsm_state <= SM_MATMUL_FSM_S9;
                end
            end
            SM_MATMUL_FSM_S9 : begin
                mem_wdata <= acc;
                mem_addr <= c_ij;
                mem_write <= 1;
                mem_req <= 1;
                b_0j <= b_0j + 1;
                c_ij <= c_ij + 1;
                j <= j + 1;
                matmul_fsm_state <= SM_MATMUL_FSM_S10;
            end
            SM_MATMUL_FSM_S10 : begin
                mem_req <= 0;
                if (bCOLS != j) begin
                    a_ik <= a_i0;
                    b_kj <= b_0j;
                    acc <= 0;
                    k <= 0;
                    matmul_fsm_state <= SM_MATMUL_FSM_S4;
                end
                else begin
                    a_i0 <= a_i0 + aSTRIDE;
                    c_i0 <= c_i0 + cSTRIDE;
                    i <= i + 1;
                    matmul_fsm_state <= SM_MATMUL_FSM_S2;
                end
            end
            SM_MATMUL_FSM_S11 : begin
                matmul_fsm_state <= SM_MATMUL_FSM_S0;
            end
        endcase
    end
end

endmodule

