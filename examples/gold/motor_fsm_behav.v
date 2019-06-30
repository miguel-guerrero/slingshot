//----------------------------------------------------------------------------
// motor_fsm
//----------------------------------------------------------------------------
module motor_fsm (
    input activate,
    input clk,
    input dn_limit,
    input rst_n,
    input up_limit,
    output reg motor_dn,
    output reg motor_up
);



`define WFE begin @(posedge clk or negedge rst_n); if (~rst_n) disable _loop; end;
always @(posedge clk or negedge rst_n) begin : control_clocked
    if (rst_n) begin : _loop
        while (1) begin
            while (~activate) begin
                `WFE
            end
            if (up_limit) begin
                motor_dn <= 1;
                `WFE
                while (~dn_limit) begin
                    `WFE
                end
                motor_dn <= 0;
            end
            else begin
                motor_up <= 1;
                `WFE
                while (~up_limit) begin
                    `WFE
                end
                motor_up <= 0;
            end
            `WFE
        end
    end
    motor_dn <= 0;
    motor_up <= 0;
    `WFE
end

endmodule


