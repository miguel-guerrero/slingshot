
# TRIP (Template Rendering In Python)

Trip is a template renderer that allows you to intermix python with source text. 
It is similar to Mako and Jinja2 widely used to generate web pages dynamically
but is lighter and more focused on the pre-preocessing needs required to
generate source code like an HDL.

# Embedding a block of python code

The following is an example

    <%
    code line 1
    code line 2
    %>

indentation is important and must match the expected one based on the previous
code

if you need to generate a verbatim piece of output use emit:

    <%
    for i in range(5):
      emit(f'---- {i} ----')
    %>


# Interpolating a python variable or an expression

The following example:

    3*8 = {{3*8}}

will generate:

    3*8 = 24

or

    <%
    x=1
    y=2
    %>

    x + y = {{x+y}}

will print

    x + y = 3


# Embedding a line of python

    % (with a space after) is to insert python code

use 'end' instead of unindent when needed to resolve indentation anbiguity. For example in the
following may seem ambiguous:

    % if x>0:
    aaa
    %   if y<0:
    %      x+=1
    bbb  

is bbb covered by the 2nd if?
it is a bit ambiguous as the emits() implicit in the non-python lines have no indentation. 
By default they are assumed to belong to the innermost block opened in python, but to 
clarify this or to force non-default behavior, you may need to insert explicit end's, for example:


    % if x>0:
    aaa
    %   if y<0:
    %      x+=1
    %   end
    bbb  

OR (this is equivalent to the default)

    % if x>0:
    aaa
    %   if y<0:
    %      x+=1
    bbb  
    %   end


# Usage

Trip can be imported as a module and used to render template strings passed to it. 

- See renderFile() and render() calls

Additionaly if used as a command, trip.py can be used to render templates from command line.

    $ trip.py --help 

for usage details
