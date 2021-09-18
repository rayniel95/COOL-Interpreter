# About

The idea of this project is to create a [COOL](https://en.wikipedia.org/wiki/Cool_(programming_language)) interpreter with type inference functionality. COOL is a strong, statically typed programming language, in this project I extend the built in types adding an AUTO_TYPE, this type inform to the interpreter that it is necessary to make a type inference for this. This mean that the AUTO_TYPE is turned into other type before code execution.

## See more

See:

- orden.pdf.

# How to execute

The test cases ending with `- copia.cl` use AUTO_TYPE. The test cases without `- copia.cl` do not use AUTO_TYPE.

Build image: `docker build ./ -t rayniel95/cool-interpreter:v1.0`

Execute: `docker run --rm --mount type=bind,source="absolute/path/to/repository",destination="/usr/src/app" -it rayniel95/cool-interpreter:v1.0 python main.py "./test_cases/<test-case-name>.cl"`

# Requirements

Docker

**Note:** this interpreter can be improved, example --> take a look to if/else block.
