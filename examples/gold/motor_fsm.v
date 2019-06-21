//----------------------------------------------------------------------------
// motor_fsm
//----------------------------------------------------------------------------
module motor_fsm (
    output reg motor_up_q,
    output reg motor_dn_q,
    input activate,
    input clk,
    input dn_limit,
    input rst_n,
    input up_limit
);

// types
localparam SM_CONTROL_S0=0;
localparam SM_CONTROL_S1=1;
localparam SM_CONTROL_S2=2;

reg [1:0] control_state;
reg [1:0] control_state_q;
reg motor_dn;
reg motor_up;

always @(posedge clk or negedge rst_n) begin
    if (~rst_n) begin
        control_state <= 0;
        control_state_q <= SM_CONTROL_S0;
        motor_dn <= 0;
        motor_dn_q <= 0;
        motor_up <= 0;
        motor_up_q <= 0;
    end
    else begin : control
        motor_dn = motor_dn_q;
        motor_up = motor_up_q;
        control_state = control_state_q;
        case (control_state)
            SM_CONTROL_S0 : begin
                if (~activate) begin
                    // stay
                end
                else begin
                    if (up_limit) begin
                        motor_dn = 1;
                        control_state = SM_CONTROL_S1;
                    end
                    else begin
                        motor_up = 1;
                        control_state = SM_CONTROL_S2;
                    end
                end
            end
            SM_CONTROL_S1 : begin
                if (~dn_limit) begin
                    // stay
                end
                else begin
                    motor_dn = 0;
                    control_state = SM_CONTROL_S0;
                end
            end
            SM_CONTROL_S2 : begin
                if (~up_limit) begin
                    // stay
                end
                else begin
                    motor_up = 0;
                    control_state = SM_CONTROL_S0;
                end
            end
        endcase
        motor_dn_q <= motor_dn;
        motor_up_q <= motor_up;
        control_state_q <= control_state;
    end
end

endmodule

