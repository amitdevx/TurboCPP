<div align="center">

![TurboC++](https://upload.wikimedia.org/wikipedia/commons/1/16/Turbo_CPP_Compiler.jpg)

**A modern port of Borland Turbo C++ 3.0 running on DOSBox for Linux and Windows**

### AI-Assisted Turbo C++ Development

Generate Turbo C++ compatible ANSI C code directly inside the IDE using `@ai` prompts.

[Features](#features) • [AI Code Generation](#ai-code-generation) • [Installation](#installation) • [Usage](#usage)

</div>

---

## Features

### AI Code Generation

* Generate complete Turbo C++ programs using `@ai`
* Generate code snippets inside existing projects
* OpenRouter integration
* Supports Gemini, DeepSeek, Llama, Qwen, and other models
* Produces Turbo C++ compatible ANSI C (C89) code
* Automatic file watching and code insertion

### Core Features

* Linux and Windows support
* DOSBox-based execution
* CPU cycle optimization
* Support for paths containing spaces
* Automated test suite
* GitHub Actions CI/CD integration
* One-command startup scripts

---

## AI Code Generation

Write prompts directly inside source files:

```c
/* @ai create a student management system */
```

Save the file and the AI engine automatically generates Turbo C++ compatible code.

### Example Use Cases

```c
/* @ai create a menu driven calculator */
```

```c
/* @ai implement bubble sort for this array */
```

```c
/* @ai create a file handling program */
```

```c
/* @ai create a linked list implementation */
```
## Features

* ✅ **Cross-Platform**: Works on Linux and Windows
* ✅ **CPU Optimized**: Cycle capping prevents high CPU usage
* ✅ **Easy Setup**: Single command to launch
* ✅ **Path Handling**: Supports directory names with spaces
* ✅ **Automated Testing**: 5 comprehensive test suites
* ✅ **CI/CD Ready**: GitHub Actions workflow included
* ✅ **AI-Powered Development**: Generate Turbo C++ compatible code directly inside the editor using `@ai` prompts
* ✅ **ANSI C Compatible Output**: Generated code follows Turbo C++ 3.0 conventions and C89 standards

---

## Improvements Over Original

| Feature             | Original   | This Version              |
| ------------------- | ---------- | ------------------------- |
| CPU Usage           | 100% (max) | ~30% (capped)             |
| Windows Support     | ❌ No       | ✅ Yes                     |
| Path Spacing        | ❌ Breaks   | ✅ Supported               |
| Tests               | ❌ No       | ✅ 5 Tests                 |
| CI/CD               | ❌ No       | ✅ GitHub Actions          |
| AI Code Generation  | ❌ No       | ✅ In-Editor `@ai` Prompts |
| OpenRouter Support  | ❌ No       | ✅ Yes                     |
| C89 Code Generation | ❌ No       | ✅ Yes                     |

---

## AI Code Generation

One of the major additions in this project is built-in AI-assisted code generation.

Write `@ai` inside any `.c` or `.cpp` file and TurboCPP can automatically generate Turbo C++ compatible code using modern AI models through OpenRouter.

### Examples

```c
/* @ai create a menu driven calculator */
```

```c
/* @ai create a student management system */
```

```c
/* @ai implement bubble sort for this array */
```

```c
/* @ai create a linked list program */
```

Generated code is designed specifically for Turbo C++ 3.0 and follows ANSI C (C89) conventions.
