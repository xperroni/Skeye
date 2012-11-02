Skeye is a programming framework developed specifically for the purpose of studying the multichannel neuron model. Currently in its early stages of development, it is written in Python, on top of third-party packages NumPy and SciPy. The combination of Python, NumPy and SciPy makes for agile development without sacrificing speed too much. Its architecture can be divided in two layers: the base package `skeye` implements the platform's core logic as a loosely-coupled library of processing functions, which in turn are used as building blocks to implement the `skeye.cogs` framework. The motivation for this division is that no one framework will be applicable to all problems: therefore, rather than try and shoehorn problems into a model that doesn't quite fit, it's best if the user can take a step back and tap into a set of building blocks from which she can build a more customized solution. It also provides a foundation for additional frameworks to be built into the platform in the future.

Functions in the base package can be divided in three categories:

* Data processing algorithms -- these implement the biological- and cognitive-inspired algorithms that prompted the development of Skeye;
* Data processing facilities -- these implement common operations that simplify the construction of more complex functions;
* Programming facilities -- these implement common programming patterns (e.g. conversions between data types) that simplify basic programming tasks.

Data processing algorithms include functions such as `bayer(image)`, which converts a 3-dimensional color image to a 2-dimensional Bayer mosaic, and `templatesearch(image, template)`, which searches for a template within a larger image. Data processing facilities include `angle(a, b)`, which returns the cosine of the angle between two vectors `a` and `b`. Programming facilities include `snapshot(image)`, which converts an image in the Python Imaging Library (PIL) format to a NumPy equivalent, and `effectors.desktop(command, *arguments, **options)`, which implements a small set of desktop automation operations.

The `skeye.cogs` package is centered around the `cogbot` class (short for `cog`nitive ro`bot`). Cogbots are simple programmable agents that can be described in terms of a predefined _memory_ defining the agent's initial state, and a sequence of _commands_ that implement its behavior, interacting with both the memory and surrounding environment as they run. When a Cogbot is activated, it executes its commands sequentially, returning a list of the commands' outputs after it finishes.
