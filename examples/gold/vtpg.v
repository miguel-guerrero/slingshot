//----------------------------------------------------------------------------
// vtpg
//----------------------------------------------------------------------------
module vtpg 
#(
    parameter H_BITS = 12,
    parameter PW = 8,
    parameter V_BITS = 12)
(
    input clk,
    input rst_n,
    input [H_BITS-1:0] tHACT_END,
    input [H_BITS-1:0] tHACT_START,
    input [H_BITS-1:0] tHS_END,
    input [H_BITS-1:0] tHS_START,
    input [H_BITS-1:0] tH_END,
    input [V_BITS-1:0] tVACT_END,
    input [V_BITS-1:0] tVACT_START,
    input [V_BITS-1:0] tVS_END,
    input [V_BITS-1:0] tVS_START,
    output reg hs,
    output reg [3*PW-1:0] rgb,
    output reg vld,
    output reg vs
);

// types
localparam SM_CONTROL_S0=0;
localparam SM_CONTROL_S1=1;
localparam SM_CONTROL_S2=2;

reg [PW-1:0] cnt;
reg [1:0] control_state;
reg [H_BITS-1:0] x;
reg [V_BITS-1:0] y;
reg y_active;


always @(posedge clk or negedge rst_n) begin : control_clocked
    if (~rst_n) begin
        cnt <= 0;
        control_state <= SM_CONTROL_S0;
        hs <= 0;
        vld <= 0;
        vs <= 0;
        x <= 0;
        y <= 0;
        y_active <= 0;
    end
    else begin
        case (control_state)
            SM_CONTROL_S0 : begin
                // hs setting
                if (tHS_START == x) begin
                    hs <= 1;
                end
                else if (tHS_END == x) begin
                    hs <= 0;
                end
                // vld setting
                if (tHACT_START == x) begin
                    vld <= y_active;
                end
                else if (tHACT_END == x) begin
                    vld <= 0;
                end
                // cnt increment
                if (vld) begin
                    cnt <= cnt + 1;
                end
                x <= x + 1;
                control_state <= SM_CONTROL_S1;
            end
            SM_CONTROL_S1 : begin
                if (tH_END != x) begin
                    // hs setting
                    if (tHS_START == x) begin
                        hs <= 1;
                    end
                    else if (tHS_END == x) begin
                        hs <= 0;
                    end
                    // vld setting
                    if (tHACT_START == x) begin
                        vld <= y_active;
                    end
                    else if (tHACT_END == x) begin
                        vld <= 0;
                    end
                    // cnt increment
                    if (vld) begin
                        cnt <= cnt + 1;
                    end
                    x <= x + 1;
                    // stay
                end
                else begin
                    if (tVS_START == y) begin
                        vs <= 1;
                    end
                    else if (tVS_END == y) begin
                        vs <= 0;
                    end
                    if (tVACT_START == y) begin
                        y_active <= 1;
                    end
                    else if (tVACT_END == y) begin
                        y_active <= 0;
                    end
                    y <= y + 1;
                    x <= 0;
                    control_state <= SM_CONTROL_S2;
                end
            end
            SM_CONTROL_S2 : begin
                if (tVACT_END != y) begin
                    // hs setting
                    if (tHS_START == x) begin
                        hs <= 1;
                    end
                    else if (tHS_END == x) begin
                        hs <= 0;
                    end
                    // vld setting
                    if (tHACT_START == x) begin
                        vld <= y_active;
                    end
                    else if (tHACT_END == x) begin
                        vld <= 0;
                    end
                    // cnt increment
                    if (vld) begin
                        cnt <= cnt + 1;
                    end
                    x <= x + 1;
                    control_state <= SM_CONTROL_S1;
                end
                else begin
                    control_state <= SM_CONTROL_S0;
                end
            end
        endcase
    end
end


always @(*) begin
    rgb = {cnt, cnt, cnt};
end


endmodule


