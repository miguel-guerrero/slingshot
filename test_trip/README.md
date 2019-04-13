
# TRIP (Template Rendering In Python)

Trip is a template renderer that allows you to intermix python with source text. 
It is similar to Mako and Jinja2, widely used to generate web pages dynamically,
but is lighter and more focused on providing clear error messages. The feature set
is expected to be adecuate for the typical needs of generating HDL.

# Embedding a block of python code

The following is an example

    <%
    python code line 1
    python code line 2
    %>

Indentation is important, as it is in python, and must match the expected one based on 
the previous code.

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

will generate:

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

# Generating code within a python block

Sometimes there is a region of the source file where there is more python than actual target
language text. It becomes inconvenient then to have to switch back and forth. 
If you need to generate a piece of output from python code you can use emit(str):

    <%
    for i in range(5):
      emit(f'---- {i} ----')
    %>

# Usage

Trip can be imported as a module and used to render template strings passed to it. 

- See renderFile() and render() calls

Additionaly if used as a command, trip.py can be used to render templates from command line.

    $ trip.py --help 

for usage details
