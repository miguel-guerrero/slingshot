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
    output reg rgb_vld,
    output reg vs
);

reg [PW-1:0] cnt;
reg [H_BITS-1:0] x;
reg [V_BITS-1:0] y;
reg y_active;

`define WFE begin @(posedge clk or negedge rst_n); if (~rst_n) disable _loop; end;

always @(posedge clk or negedge rst_n) begin : control_clocked
    if (rst_n) begin : _loop
        while (1) begin
            do begin
                do begin
                    // create h sync
                    if (tHS_START == x) begin
                        hs <= 1;
                    end
                    else if (tHS_END == x) begin
                        hs <= 0;
                    end
                    // rgb_vld setting
                    if (tHACT_START == x) begin
                        rgb_vld <= y_active;
                    end
                    else if (tHACT_END == x) begin
                        rgb_vld <= 0;
                    end
                    // pixel cnt increment
                    if (rgb_vld) begin
                        cnt <= cnt + 1;
                    end
                    x <= x + 1;
                    `WFE
                end while (tH_END != x);
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
                `WFE
            end while (tVACT_END != y);
            `WFE
        end
    end
    cnt <= 0;
    hs <= 0;
    rgb_vld <= 0;
    vs <= 0;
    x <= 0;
    y <= 0;
    y_active <= 0;
    `WFE
end

always @(*) rgb = {cnt, cnt, cnt};

endmodule


