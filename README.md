
# INTRODUCTION

This repo is a tool to generate HDL (Hardware Description Language) code 
in python. It is influenced by the following [awesome] projects:

- Genesis2: 

   https://github.com/StanfordVLSI/Genesis2

   Provided main concepts/benefits of hierarchical generation + instrospection

   Created by Ofer Shacham in Stanford as part of his PhD work.

    - Overview “Creating Chip Generators for Efficient Computing at Low 
      NRE Design Costs”
    - PhD Thesis “Chip Multiprocessor Generator: Automatic Generation Of 
      Custom And Heterogeneous Compute Platforms”
    - More info:  http://genesis2.stanford.edu/mediawiki/index.php/Genesis2

- Pyverilog:

    https://pypi.org/project/pyverilog

    Provided interesting ideas about building HW through an API 
    (application program interface). 

    Takamaeda-Yamazaki S. (2015) Pyverilog: A Python-Based Hardware Design 
    Processing Toolkit for Verilog HDL. In: Sano K., Soudris D., Hübner M., 
    Diniz P. (eds) Applied Reconfigurable Computing. ARC 2015. 
    Lecture Notes in Computer Science, vol 9040. Springer, Cham

- Migen: a python based HCL (Hardware Creation Language)

    https://github.com/m-labs/migen

    Some syntax elements are inspired on it


Additionaly this project has the following goals:

- Readability of generated code specially at leaf level
- Full Introspection and flexibility
- Ease / brevety of input with focus on leaf level code
- Readability of input

# CONTENTS

It is composed of the following interelated and interoperating modules:

- Trip: (Template Rendering In Python)

    A python based preprocessor used by G@P. It is similar to Mako/jinja2 but 
    simpler and self contained. Intends to capture the usecases more important 
    for HW generation and provide more focused error messages.

- G2P (Genesis2 in Python)

    Hierarchical code generator with introspection, uses Trip and can use 
    also Mako as template rendering engine. Target HDL is mixed with 
    pre-processor style code in python. A descendent of Genesis2
    but not intended to be feature complete or backwards compatible.

- Chipo: (Contruction of Hardware In Python Only)

    Started as an API to encapsulate comon operations in G2P, evolved into an API
    to build an AST before being dumped as text into G2P and finally evolved into
    a embedded DSL that captures a module AST fully in python. This last approach
    allows further trasnformations to the AST before being dumped

    Can interoperate with G2P so both approaches can be used in the same design.


Other:

- gencore.py:
  Contains common base clases to allow G2P/Chipo interoperation

- regs.py:
  Experimental approach to allow control/status registers to be defined bottom-up.
  Currently at proof of concept level for simple registers but proven in one design.
  Optionally used by Chipo

- varname.py:
  Utility to find out a variable name at run time. Used by Chipo.


# DEPENDENCIES

- iverilog: this open source simulator is used to compile and simulate, in some 
  cases, the generated code. Follow the instructions in the following link for 
  installation:

  http://iverilog.icarus.com

- Python 3. The project is currently tested with Python 3.6.5


# LICENSE

See LICENSE and NOTICE files for licensing details

