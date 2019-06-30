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

// types
localparam SM_CONTROL_S0=0;
localparam SM_CONTROL_S1=1;
localparam SM_CONTROL_S2=2;

reg [1:0] control_state;

always @(posedge clk or negedge rst_n) begin : control_clocked
    if (~rst_n) begin
        control_state <= SM_CONTROL_S0;
        motor_dn <= 0;
        motor_up <= 0;
    end
    else begin
        case (control_state)
            SM_CONTROL_S0 : begin
                if (~activate) begin
                    // stay
                end
                else begin
                    if (up_limit) begin
                        motor_dn <= 1;
                        control_state <= SM_CONTROL_S1;
                    end
                    else begin
                        motor_up <= 1;
                        control_state <= SM_CONTROL_S2;
                    end
                end
            end
            SM_CONTROL_S1 : begin
                if (~dn_limit) begin
                    // stay
                end
                else begin
                    motor_dn <= 0;
                    control_state <= SM_CONTROL_S0;
                end
            end
            SM_CONTROL_S2 : begin
                if (~up_limit) begin
                    // stay
                end
                else begin
                    motor_up <= 0;
                    control_state <= SM_CONTROL_S0;
                end
            end
        endcase
    end
end

endmodule


