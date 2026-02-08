# 🔗 mc-execute - API Documentation

---

## 1. Execute Class

The `Execute` class manages the execution context (position, rotation, dimension, and executor). It supports method chaining to mimic the flow of Minecraft `execute` commands.

### Context Forking

When passing a list of entities to methods like `as_`, `at`, `facing`, `positioned`, or `rotated`, `Execute` performs a Cartesian product between the current contexts and the target entities. This results in the "forking" behavior seen in Minecraft (e.g., `execute as @a`).

### Constructor & Properties

| Member | Type | Description |
| :--- | :--- | :--- |
| **`__init__(target)`** | target: `Execute \| Entity \| None` | Initializes the context. If `None`, starts at the server default ([0., 0., 0.] in the Overworld without entity). |
| **`entities`** | `list[Entity \| None]` | A list of entities currently "executing" the command in each context. |
| **`positions`** | `np.ndarray` | An `(N, 3)` array of positions for all contexts. (dtype: `np.float64`) |
| **`rotations`** | `np.ndarray` | An `(N, 2)` array of rotations (yaw, pitch) for all contexts. (dtype: `np.float32`) |
| **`dimensions`** | `list[Dimension]` | A list of dimensions for each context. |

### Methods

*All methods return `self` to support chaining.*

- `arg` parameter can be  an Entity, a list of Entity, a numpy array, string coordinates, or "@s".

| Method | Parameters | Description |
| :--- | :--- | :--- |
| **`align`** | `axes` | Snaps coordinates to the block grid (`floor`) for specified axes (e.g., `"xyz"`). |
| **`anchored`** | `anchor` | Sets the local anchor point to `feet` or `eyes` for future coordinate calculations. |
| **`as_`** | `target` | Changes the executor. Passing a list forks the context. |
| **`at`** | `target` | Updates position, rotation, and dimension to match the target(s). Supports `"@s"`. |
| **`facing`** | `arg, anchor` | Rotates the context to face a specific coordinate or entity. |
| **`in_`** | `dimension` | Changes the dimension of all current contexts. |
| **`positioned`** | `arg` | Updates the position only. Supports absolute, relative (`~`), or local (`^`) coordinate strings. |
| **`rotated`** | `arg` | Updates the rotation only. Can target an entity's rotation or a specific `yaw pitch` string. |

---

## 2. Entity Class

The `Entity` class represents an individual object in the world. It holds physical state data and can be used to capture the results of an `Execute` chain.

### Constructor & Attributes

| Member | Type | Description |
| :--- | :--- | :--- |
| **`__init__(target)`** | target: `Execute \| Entity` | Initializes the context. If `Execute`, only the last context from target `Execute` will be applied during initialization. |
| **`position`** | `np.ndarray` | `[x, y, z]` NumPy array (`np.float64`). |
| **`rotation`** | `np.ndarray` | `[yaw, pitch]` NumPy array (`np.float32`). |
| **`dimension`** | `Dimension` | The current `Dimension` enum value. |
| **`eye_level`** | `np.float64` | Offset added to `position` when using `EntityAnchor.eyes`. |

### Methods

| Method | Parameters | Description |
| :--- | :--- | :--- |
| **`setEyeLevel`** | `height` | Sets the vertical offset for the entity's eyes. |
| **`getAnchoredPosition`** | `anchor` | Returns the position adjusted for the specified anchor (`feet` or `eyes`). |
| **`tp`** | `pos, dimension` | Teleports the entity. Supports 3-value strings (`"x y z"`) or 5-value strings (`"x y z yaw pitch"`). |
| **`rotate`** | `rot` | Updates the entity's rotation. Supports relative rotation strings (e.g., `"~10 ~"`). |
| **`setDimension`** | `dimension` | Directly moves the entity to a different dimension. |
