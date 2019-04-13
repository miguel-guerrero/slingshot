
# Introduction

In a g2p file to be processed, functions/classes in g2p as imported with namespace 'g', equivalent to

    import g2p as g

being implicitly present


# Predefined variables (on current namespace)

The following variables have a special meaning and must be handled for
correct generation

## As inputs:

*passedParamDict*: 

A dictionary containing all passed down parameters


## As mandatory outputs:

**paramDict**: 

The user should merge passedParamDict and default parameters
into this one representing the final set of parameters including
overrides

**name**: 

The uniquified name of the module. It is usually computed as a base name
and as a function of all the parameters passed and defaults.

An example of the recommended fool proof way of getting the above:

    defaultParamDict = {'CNT':8, 'WIDTH':32, 'HAS_CIN':0}
    name, params, paramDict = g.processParams('multi_adder3', passedParamDict, defaultParamDict)

Note that params is not predefined, but if using this function, it provides
a second way to access the final parameters as a class generated from paramDict

g.procesParams generates name including only parameters that have been
overridden or parameters that had no default appending them to the 
base name in alphabetical order as name-value pairs


**IOs**: 

A list filled up by the user with all IOs of the module. Use following
constructors to create them:

        g.Input(name, width=1, lsb=0)
        g.Output(name, width=1, lsb=0)

The function g.vlogIO(IOs) can be used to return the IO definitions of a module in Verilog
format as a string (the user can render it in the appropriate place)


**result**: 

It is internally managed and will be overwritten if given a value by the
user, when the generation of the module ends it gets a copy of the 
following object. The user shouldn't write it, it is intended as an output.

        g.Module(name, IOs, paramDict, instances.thisLevel(), userResult)

instances is an object that allows the creation of instances at 
this level of hierarchy by using
    
        instances.new(basename, passParamDict)
    
and tracks everything instantiated. Those instances are available as a list
as:

        instances.thisLevel()

## As optional outputs:

**userResult**: 

to be filled by the user with whatever information needs
to carry to the parent. It defaults to an instance of

    class UserResult():
        pass

the user can override the type or just add fields to it as follows:

for instance. 

    userResult.ff_count = 10


