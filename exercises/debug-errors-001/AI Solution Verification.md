# AI Solution Verification — Merge Sort Bug

## Chosen problem — Buggy `mergeSort` function

---

## The buggy code

```js
function merge(left, right) {
  let result = [];
  let i = 0;
  let j = 0;

  while (i < left.length && j < right.length) {
    if (left[i] < right[j]) {
      result.push(left[i]);
      i++;
    } else {
      result.push(right[j]);
      j++;
    }
  }

  // Bug: incrementing j instead of i in this loop
  while (i < left.length) {
    result.push(left[i]);
    j++;  // <-- should be i++
  }

  while (j < right.length) {
    result.push(right[j]);
    j++;
  }

  return result;
}
```

The bug: in the `while (i < left.length)` tail loop, `j++` is written instead of `i++`. Since `i` never increments, the loop is infinite. Since `j` keeps incrementing past `left.length`, eventually either `result` grows to absurd size or the script hangs.

---

## Verification strategy 1: Collaborative Solution Verification

### Process

I prompted an AI to produce a merge sort implementation. The AI returned standard merge sort code. I then cross-validated by:

1. Running the code through a **manual trace** with a small input (`[3, 1, 2]`)
2. Checking each loop invariant against the standard merge algorithm
3. Writing a **simple test harness** (below)

### Test harness

```js
function testMergeSort() {
  const tests = [
    { input: [3, 1, 2], expected: [1, 2, 3] },
    { input: [], expected: [] },
    { input: [1], expected: [1] },
    { input: [5, 3, 8, 1, 9, 2], expected: [1, 2, 3, 5, 8, 9] },
    { input: [1, 2, 3, 4, 5], expected: [1, 2, 3, 4, 5] },
    { input: [5, 4, 3, 2, 1], expected: [1, 2, 3, 4, 5] },
  ];

  for (const { input, expected } of tests) {
    const result = mergeSort([...input]);
    const pass = JSON.stringify(result) === JSON.stringify(expected);
    console.log(`${pass ? 'PASS' : 'FAIL'} | [${input}] => [${result}] ${pass ? '' : `(expected [${expected}])`}`);
  }
}
```

Running this immediately reveals the bug — the first test hangs or crashes, or produces `[1, 2, 3, undefined, undefined, ...]` depending on the JS engine.

### How confidence changed

**Before verification:** High confidence — the merge sort structure looks correct at a glance, and the AI-generated code follows the standard pattern.

**After trace + test:** Confidence dropped to zero. The specific loop-variable typo is invisible to a reader who isn't carefully checking variable names in the tail loops.

**After fix + retest:** Confidence back to high — all 6 test cases pass.

---

## Verification strategy 2: Learning Through Alternative Approaches

### Process

I asked the AI to produce an **iterative (bottom-up) merge sort** and a **different merge implementation** to compare approaches.

### Alternative A: Bottom-up iterative merge sort

```js
function mergeSortIterative(arr) {
  if (arr.length <= 1) return arr;

  let n = arr.length;
  let result = [...arr];

  for (let size = 1; size < n; size *= 2) {
    for (let leftStart = 0; leftStart < n; leftStart += 2 * size) {
      let mid = Math.min(leftStart + size, n);
      let rightEnd = Math.min(leftStart + 2 * size, n);
      mergeInPlace(result, leftStart, mid, rightEnd);
    }
  }

  return result;
}

function mergeInPlace(arr, start, mid, end) {
  let left = arr.slice(start, mid);
  let right = arr.slice(mid, end);
  let i = 0, j = 0, k = start;

  while (i < left.length && j < right.length) {
    arr[k++] = left[i] <= right[j] ? left[i++] : right[j++];
  }
  while (i < left.length) arr[k++] = left[i++];
  while (j < right.length) arr[k++] = right[j++];
}
```

### What this revealed

The iterative version avoids recursion entirely and uses a different merge strategy (in-place via slice). Crucially, both tail loops in `mergeInPlace` correctly increment `i` and `j` respectively — no typo opportunity in the same place. Comparing the two implementations confirmed the **correct pattern** for the tail loops:

```
while (i < left.length)  → increment i
while (j < right.length) → increment j
```

This made the bug in the original code obvious: **the first tail loop mutates `j` when it should mutate `i`**.

---

## Verification strategy 3: Developing a Critical Eye

### Process

I reviewed the AI's solution line-by-line, specifically **reading with suspicion** at common bug-prone locations:

1. **Loop bounds and increment variables** — are the correct index variables being updated?
2. **Copy-paste symmetry** — the two tail loops are structurally identical except for `i`/`j`. Did the pattern get propagated correctly?
3. **Edge cases** — empty array, single element, already sorted, reverse sorted, duplicates

### Findings

| Check | Result |
|-------|--------|
| Base case (`arr.length <= 1`) | Correct |
| Midpoint calculation | Correct |
| Recursive division | Correct |
| Main merge loop condition (`i < left.length && j < right.length`) | Correct |
| First tail loop condition (`i < left.length`) | Correct |
| **First tail loop increment** | **BUG — `j++` instead of `i++`** |
| Second tail loop condition (`j < right.length`) | Correct |
| Second tail loop increment | Correct |

The pattern that caught the bug: **the first tail loop reads from `left[i]` but increments `j`**. A reader expecting symmetry sees:

```
// Tail loop for left — should mirror the pattern:
result.push(left[i]); i++;
// But actually writes:
result.push(left[i]); j++;
```

The mismatch between the array being read (`left[i]`) and the variable being incremented (`j`) is the fingerprint of a copy-paste error.

### What made this bug subtle

- The code *looks* correct because both tail loops exist and the structure is standard
- A human reviewer skims the tail loops and sees the pattern "push then increment" without checking *which* variable is incremented
- The AI that generated this likely produced the typo from a pattern-completion error in its own generative process

---

## Final verified solution

```js
function mergeSort(arr) {
  if (arr.length <= 1) return arr;

  const mid = Math.floor(arr.length / 2);
  const left = mergeSort(arr.slice(0, mid));
  const right = mergeSort(arr.slice(mid));

  return merge(left, right);
}

function merge(left, right) {
  const result = [];
  let i = 0;
  let j = 0;

  while (i < left.length && j < right.length) {
    if (left[i] <= right[j]) {
      result.push(left[i]);
      i++;
    } else {
      result.push(right[j]);
      j++;
    }
  }

  // Flatten remaining elements from whichever side has leftovers
  while (i < left.length) {
    result.push(left[i]);
    i++;
  }

  while (j < right.length) {
    result.push(right[j]);
    j++;
  }

  return result;
}
```

Changes from the buggy version:
1. **`j++` → `i++`** in the first tail loop (fixes the infinite loop / wrong output)
2. **`left[i] < right[j]` → `left[i] <= right[j]`** in the comparison (makes the sort **stable** — equal elements retain their original order)
3. **`let result = []` → `const result = []`** (the array reference never changes, only mutation, so `const` is more precise)

All test cases pass with the fixed implementation.

---

## Reflection

### How confidence changed after verification

I went from **"looks right, it's merge sort"** (high confidence) → **"the tests hang — something is wrong"** (zero confidence) → **"the typo is obvious once you test"** → **"verified with 6 test cases, two algorithm variants, and line-by-line review"** (high confidence). The key inflection was running the test harness — the code had passed my visual review entirely.

### What aspects required the most scrutiny

The **loop variables in the tail loops** required the most scrutiny because they look identical at a glance. Both loops follow the pattern `while (X < X.length) { result.push(X[X]); X++; }`, and a reader's brain fills in the symmetry automatically. Actively checking that each loop increments the *same variable it reads* is the only way to catch this.

### Which verification technique was most valuable

**Collaborative Solution Verification (tests)** was the most valuable — it revealed the bug immediately with zero speculation. The test harness took 30 seconds to write and instantly exposed the problem. The **Critical Eye** review confirmed it, and **Alternative Approaches** confirmed the correct pattern by comparison. Without tests, this bug would have been easy to miss in code review.
