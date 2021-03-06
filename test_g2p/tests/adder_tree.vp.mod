// passedParamDict ${passedParamDict}
<%

from math import ceil, log2
defaultParamDict = {'CNT':8, 'WIDTH':32, 'HAS_CIN':0}
name, paramDict, _ = g.processParams('adder_tree', passedParamDict, defaultParamDict)
# internal parameters
treeLevels = ceil(log2(paramDict['CNT'])) - 1 
paramDict['OWIDTH'] = treeLevels + paramDict['WIDTH']
params = g.dictToObj(paramDict)

IOs = [g.Output('sum', params.OWIDTH)]
for i in range(params.CNT):
    IOs += [g.Input(f'in{i}', params.WIDTH)]
if params.HAS_CIN:
    IOs += [g.Input(f'cin{i}')]
end
%>

// defaultParamDict ${defaultParamDict}
// paramDict ${paramDict}
// name ${name}
// params.WIDTH ${params.WIDTH}
// params.OWIDTH ${params.OWIDTH}
// params.HAS_CIN ${params.HAS_CIN}
// IOs ${IOs}

module ${name}
(
    ${g.vlogIO(IOs)}
)

<%
cnt = params.CNT
pin = [f"in{i}" for i in range(cnt)]
level = 0
while len(pin) > 0:
    W = params.WIDTH+level
    mod = g.generate('adder', {'WIDTH':W})
    pout = []
   for i in range(len(pin)//2):
        ps = f"ps_{level}_{i}"
        pout += [ps]
        ins = g.Instance(mod, f'adder_{level}_{i}')
        instances.add(ins)
%>

    wire [${W-1}:0] ${ps};
    ${mod.name} ${ins.name} (
        .a(${pin[2*i]}),
        .b(${pin[2*i+1]}),
        .sum(${ps})
    )

<%
    end
    pin = pout
    level += 1
end
%>

assign sum = ${ps};

endmodule

