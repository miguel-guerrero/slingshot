//----------------------------------------------------------------------------
// fsm
//----------------------------------------------------------------------------
module fsm (
    input clk,
    input rst_n,
    output reg ctl,
    output reg done
);

// types
localparam IDLE=0;
localparam GO=1;
localparam DONE=2;

reg [1:0] state;
reg [1:0] state_nxt;

always @(*) 
    case (state)
        IDLE : begin
            state_nxt <= GO;
            ctl <= 0;
        end
        GO : begin
            state_nxt <= DONE;
            ctl <= 1;
        end
        DONE : 
            state_nxt <= IDLE;
        default: begin
            state_nxt <= IDLE;
            ctl <= 0;
        end
    endcase

always @(*) 
    done <= state == DONE;

always @(posedge clk or negedge rst_n) 
    if (~rst_n) 
        state <= 0;
    else 
        state <= state_nxt;

endmodule

