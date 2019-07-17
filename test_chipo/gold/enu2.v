//----------------------------------------------------------------------------
// fsm
//----------------------------------------------------------------------------
module fsm (
    input clk,
    input rst_n,
    output logic ctl,
    output logic done,
    output logic [1:0] state
);

// types
typedef enum logic [1:0] {IDLE=0, GO=1, DONE=2} States;

States state_nxt;


always @(*) begin
    case (state)
        IDLE : begin
            state_nxt = GO;
            ctl = 0;
        end
        GO : begin
            state_nxt = DONE;
            ctl = 1;
        end
        DONE : begin
            state_nxt = IDLE;
        end
        default: begin
            state_nxt = IDLE;
            ctl = 0;
        end
    endcase
end

assign done = state == DONE;

always @(posedge clk or negedge rst_n) begin
    if (~rst_n) begin
        state <= IDLE;
    end
    else begin
        state <= state_nxt;
    end
end


endmodule


