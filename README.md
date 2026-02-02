# 🔗 mc-execute

> Simulate Minecraft `execute` commands in a Python environment.

**mc-execute** is a library for simulating Minecraft `execute` command chains within Python.

### Features
- NumPy Integration: Provides execute context's position and rotation data as numpy arrays.
- Context Forking: Implements branching logic for commands such as `execute as` and `execute at` to match in-game behavior.
- Mathematical Consistency: Uses the same calculation logic as the game to replicate in-game precision errors.

---

### Getting Started

#### 1. Entity

Set the position, rotation, dimension, and eye level of an entity.

```python
import numpy as np
from mc_execute import Entity, Execute

# A = B = C
# summon entity: Pos:[1.5d, 2.0d, 3.5d], Rotation:[-90.0f, 0.0f]
A = Entity().tp("1 2 3 -90 0")
B = Entity().tp("1 2 3").rotate("-90 0")
C = Entity().tp(np.array([1.5, 2., 3.5], dtype=np.float64)).rotate(np.array([270., 0.], dtype=np.float32))

marker = Entity()   # same as tp("0. 0. 0.").rotate("0. 0.")
player = Entity().setDimension("overworld").setEyeLevel(1.62)
```

#### 2. Execute

Utilize method chaining similar to the syntax of Minecraft's `execute` subcommand.

```python
# execute as A at @s rotated as player positioned ^ ^ ^5
exe = Execute().as_(A).at().rotated(player).positioned("^ ^ ^5")

print(exe.positions)  # Output coordinates of all contexts
print(exe.rotations)  # Output rotations of all contexts
```

#### 3. Context Fork

Contexts are forked when a list of multiple entities is passed to branching-capable methods.

```python
# When 2 executors target 3 locations:
# execute as [A, B] at [P, Q, R] -> Generates a total of 6 contexts
exe = Execute().as_([A, B]).at([P, Q, R])

print(len(exe.positions)) # 6
```

#### 4. Context Copy/Apply

You can reapply an existing `Execute` context to a new `Execute` instance or an `Entity`. Since an `Entity` object holds a single unique context, only the last context from a branched `Execute` chain will be applied when initializing an `Entity`.

```python
exe = Execute().as_(A).at(B).facing(marker)

# Copy all contexts to a new Execute instance
exe_copied = Execute(exe)

# Apply the last context's position and rotation to the Entity
chicken = Entity(exe)
```

---

### Examples / Document

For more details, see the [example](./example.ipynb) and [API Documentation](./API_DOC.md).

---

### Licences

mc-execute provides [MIT License](./LICENSE).
