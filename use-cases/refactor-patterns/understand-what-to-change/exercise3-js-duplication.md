# Exercise 3: Code Duplication Detection (JavaScript)

## Prompt template used

```
I need to eliminate duplication in this JavaScript function. It calculates
statistics (average and highest) for age, income, and score from an array
of user objects.

For each duplication pattern you find, show the consolidated version and
explain why the refactored version is better.

Target audience: a team of junior developers — prioritize readability over
cleverness.
```

## Original code

```javascript
function calculateUserStatistics(userData) {
  // Calculate average age
  let totalAge = 0;
  for (let i = 0; i < userData.length; i++) {
    totalAge += userData[i].age;
  }
  const averageAge = totalAge / userData.length;

  // Calculate average income
  let totalIncome = 0;
  for (let i = 0; i < userData.length; i++) {
    totalIncome += userData[i].income;
  }
  const averageIncome = totalIncome / userData.length;

  // Calculate average score
  let totalScore = 0;
  for (let i = 0; i < userData.length; i++) {
    totalScore += userData[i].score;
  }
  const averageScore = totalScore / userData.length;

  // Find highest age
  let highestAge = userData[0].age;
  for (let i = 1; i < userData.length; i++) {
    if (userData[i].age > highestAge) {
      highestAge = userData[i].age;
    }
  }

  // Find highest income
  let highestIncome = userData[0].income;
  for (let i = 1; i < userData.length; i++) {
    if (userData[i].income > highestIncome) {
      highestIncome = userData[i].income;
    }
  }

  // Find highest score
  let highestScore = userData[0].score;
  for (let i = 1; i < userData.length; i++) {
    if (userData[i].score > highestScore) {
      highestScore = userData[i].score;
    }
  }

  return {
    age: {
      average: averageAge,
      highest: highestAge
    },
    income: {
      average: averageIncome,
      highest: highestIncome
    },
    score: {
      average: averageScore,
      highest: highestScore
    }
  };
}
```

## Duplication patterns identified

### Pattern 1: Three identical "sum" loops

Lines 3-7, 10-14, and 17-21 are identical except for the field name (`age`, `income`, `score`):

```javascript
let totalX = 0;
for (let i = 0; i < userData.length; i++) {
  totalX += userData[i].X;
}
const averageX = totalX / userData.length;
```

The AI suggested two approaches:

**Approach A — extract a `sum` helper:**
```javascript
function sumByField(data, field) {
  return data.reduce((total, item) => total + item[field], 0);
}
```

**Approach B — extract a `calculateAverage` helper:**
```javascript
function calculateAverage(data, field) {
  return sumByField(data, field) / data.length;
}
```

### Pattern 2: Three identical "maximum" loops

Lines 23-27, 30-34, and 37-41 are identical except for the field name:

```javascript
let highestX = userData[0].X;
for (let i = 1; i < userData.length; i++) {
  if (userData[i].X > highestX) {
    highestX = userData[i].X;
  }
}
```

Extracted to:
```javascript
function highestByField(data, field) {
  return Math.max(...data.map(item => item[field]));
}
```

Or without spreading (better for large arrays):
```javascript
function highestByField(data, field) {
  return data.reduce((max, item) => Math.max(max, item[field]), -Infinity);
}
```

### Pattern 3: The entire function produces the same shape for each field

```
age    → { average: ..., highest: ... }
income → { average: ..., highest: ... }
score  → { average: ..., highest: ... }
```

The AI suggested building the result dynamically:
```javascript
function calculateFieldStats(data, field) {
  return {
    average: calculateAverage(data, field),
    highest: highestByField(data, field)
  };
}
```

## Refactored version (recommended for junior developers)

The AI recommended this version as most readable for juniors — it uses descriptive function names and avoids `reduce` in the main flow:

```javascript
function calculateUserStatistics(userData) {
  if (!userData || userData.length === 0) {
    return { age: null, income: null, score: null };
  }

  return {
    age: calculateFieldStats(userData, 'age'),
    income: calculateFieldStats(userData, 'income'),
    score: calculateFieldStats(userData, 'score'),
  };
}

function calculateFieldStats(data, field) {
  return {
    average: calculateAverage(data, field),
    highest: highestByField(data, field),
  };
}

function calculateAverage(data, field) {
  const total = data.reduce((sum, item) => sum + item[field], 0);
  return total / data.length;
}

function highestByField(data, field) {
  let highest = data[0][field];
  for (let i = 1; i < data.length; i++) {
    if (data[i][field] > highest) {
      highest = data[i][field];
    }
  }
  return highest;
}
```

## Alternative (using `reduce`)

A more compact version — less readable for juniors but a common JS pattern:

```javascript
function calculateFieldStats(data, field) {
  return {
    average: data.reduce((sum, item) => sum + item[field], 0) / data.length,
    highest: data.reduce((max, item) => Math.max(max, item[field]), -Infinity),
  };
}
```

## What the AI flagged that I might have missed

- **Empty array crash** — if `userData` is `[]`, the original code crashes at `userData[0].age` (accessing index 0 on empty array returns `undefined`, then accessing `.age` throws). The refactored version adds a guard clause at the top.
- **Single-element array edge case** — the `highest` loops start at `i = 1`, so a single-element array skips the loop. The extracted version using `data[0][field]` as initial value handles this correctly. But if I'd used `reduce` with `-Infinity`, it would also work for single-element arrays.
- **Nullish input** — if `userData` is `null`, `userData.length` throws. The guard `!userData` covers this.
- **Non-existent field** — if `userData[i].height` doesn't exist, the original would compute `average = NaN` and `highest = undefined`. The AI suggested but didn't implement a warning for missing fields.

## Which approach is most readable for juniors

The **extracted helper functions with clear names** (`calculateAverage`, `highestByField`, `calculateFieldStats`) is the best approach for juniors. Each function is:
- Short enough to read in one glance
- Named to describe what it does
- Independently testable
- Reusable across the codebase

The `reduce` version is more idiomatic JavaScript but harder for a junior to understand because `reduce` has a steeper learning curve. The `for` loop inside `highestByField` is more explicit and educational.

## What I disagree with

The AI suggested calculating `average` and `highest` in a single pass to avoid iterating the array twice per field. That optimization is valid for large datasets, but it couples the two calculations together and makes the code harder to read. For most applications, iterating 100 items twice is irrelevant. I'd keep them separate for clarity.
