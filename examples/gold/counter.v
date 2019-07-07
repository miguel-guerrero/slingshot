/*
./counter.py:17:1
      12     WIDTH = Param(cntW)
      13     clk, rst_n = Clock(), Reset()
      14     inc, clr = In() ** 2
      15     max_val = In(WIDTH)
      16     eq, cnt = Out(), Out(WIDTH)
->    17     return Module(clk, rst_n) [
      18             Combo() [
      19                 eq <= (cnt == max_val),
      20             ],
      21             Comment('clear and increment logic', 'goes here'),
      22             Clocked() [
*/
//----------------------------------------------------------------------------
// counter
//----------------------------------------------------------------------------
module counter 
#(
    parameter WIDTH = 8)
(
    input clk,
    input rst_n,
    input clr,
    input inc,
    input [WIDTH-1:0] max_val,
    output reg [WIDTH-1:0] cnt,
    output reg eq
);




/*
./counter.py:18:1
      13     clk, rst_n = Clock(), Reset()
      14     inc, clr = In() ** 2
      15     max_val = In(WIDTH)
      16     eq, cnt = Out(), Out(WIDTH)
      17     return Module(clk, rst_n) [
->    18             Combo() [
      19                 eq <= (cnt == max_val),
      20             ],
      21             Comment('clear and increment logic', 'goes here'),
      22             Clocked() [
      23                 If (clr) [
*/
always @(*) begin
    eq = cnt == max_val;
end

/*
./counter.py:21:1
      16     eq, cnt = Out(), Out(WIDTH)
      17     return Module(clk, rst_n) [
      18             Combo() [
      19                 eq <= (cnt == max_val),
      20             ],
->    21             Comment('clear and increment logic', 'goes here'),
      22             Clocked() [
      23                 If (clr) [
      24                     Comment('clear has priority'),
      25                     cnt <= 0
      26                 ].Elif (inc) [
*/
// clear and increment logic
// goes here

/*
./counter.py:22:1
      17     return Module(clk, rst_n) [
      18             Combo() [
      19                 eq <= (cnt == max_val),
      20             ],
      21             Comment('clear and increment logic', 'goes here'),
->    22             Clocked() [
      23                 If (clr) [
      24                     Comment('clear has priority'),
      25                     cnt <= 0
      26                 ].Elif (inc) [
      27                     cnt <= cnt + 1
*/
always @(posedge clk or negedge rst_n) begin
/*
./counter.py:27:1
      22             Clocked() [
      23                 If (clr) [
      24                     Comment('clear has priority'),
      25                     cnt <= 0
      26                 ].Elif (inc) [
->    27                     cnt <= cnt + 1
      28                 ]
      29             ]
      30         ].autoGen()
      31 
      32 
*/
    if (~rst_n) begin
        cnt <= 0;
    end
    else begin
/*
./counter.py:23:1
      18             Combo() [
      19                 eq <= (cnt == max_val),
      20             ],
      21             Comment('clear and increment logic', 'goes here'),
      22             Clocked() [
->    23                 If (clr) [
      24                     Comment('clear has priority'),
      25                     cnt <= 0
      26                 ].Elif (inc) [
      27                     cnt <= cnt + 1
      28                 ]
*/
        if (clr) begin
/*
./counter.py:24:1
      19                 eq <= (cnt == max_val),
      20             ],
      21             Comment('clear and increment logic', 'goes here'),
      22             Clocked() [
      23                 If (clr) [
->    24                     Comment('clear has priority'),
      25                     cnt <= 0
      26                 ].Elif (inc) [
      27                     cnt <= cnt + 1
      28                 ]
      29             ]
*/
            // clear has priority
            cnt <= 0;
        end
        else if (inc) begin
            cnt <= cnt + 1;
        end
    end
end


endmodule


