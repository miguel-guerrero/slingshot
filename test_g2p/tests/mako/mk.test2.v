<% N = passedParamDict.get('N', 12) %>
<% CNT = passedParamDict.get('CNT', 8) %>

module multi_adder(
   <% for i in range(CNT) %>
       input [${N-1}:0] a${i},
       input [${N-1}:0] b${i},
       output [${N}:0] sum${i},
       input cin${i},
   <% endfor %>
)

<% for i in range(CNT) 
   inst = g2p.generate('mk.test1.v', f'adder_{N}bits', {'N', N})
%>

   ${inst.name} ${inst_name}_${i} (
       .a(a${i}),
       .b(b${i}),
       .sum(sum${i}),
       .cout(cout${i})
   );

<% endfor %>

endmodule

