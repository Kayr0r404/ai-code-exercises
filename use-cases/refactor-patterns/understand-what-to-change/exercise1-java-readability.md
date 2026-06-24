# Exercise 1: Code Readability Improvement (Java)

## Prompt template used

```
I need to improve the readability of this Java code. Please analyze it and suggest
specific improvements following standard Java naming conventions (camelCase for methods
and variables, PascalCase for classes, UPPER_SNAKE for constants).

For each issue you find, explain why it hurts readability and show the improved version.

Focus on:
- Variable and method naming
- Class naming
- Code structure and organization
- Comments/documentation where appropriate
- SQL injection and security concerns
```

## Original code

```java
class UserMgr {
    private List<U> u_list;
    private DBConn db;

    public UserMgr(DBConn d) {
        db = d;
        u_list = new ArrayList<>();
    }

    public boolean a(String un, String pw, String em) {
        if (un.length() < 3 || pw.length() < 8 || !em.contains("@")) {
            return false;
        }

        for (U user : u_list) {
            if (user.getUn().equals(un)) {
                return false;
            }
        }

        U nu = new U(un, pw, em);
        u_list.add(nu);
        boolean res = db.execute("INSERT INTO users VALUES ('" + un + "', '" + pw + "', '" + em + "')");
        return res;
    }

    public U f(String un) {
        for (U user : u_list) {
            if (user.getUn().equals(un)) {
                return user;
            }
        }
        return null;
    }
}

class U {
    private String un;
    private String pw;
    private String em;

    public U(String un, String pw, String em) {
        this.un = un;
        this.pw = pw;
        this.em = em;
    }

    public String getUn() { return un; }
    public String getPw() { return pw; }
    public String getEm() { return em; }
}
```

## Issues identified by the AI

### 1. Class naming — cryptic abbreviations

| Issue | Original | Improved |
|-------|----------|----------|
| `UserMgr` → should be `UserManager` | Abbreviation of "Manager" reduces clarity | `UserManager` — full words |
| `U` → should be `User` | Single letter has no meaning | `User` — self-documenting |
| `DBConn` → `DatabaseConnection` or `DataSource` | Unclear what DBConn represents | `DatabaseConnection` — explicit |

### 2. Method naming — single letters

| Original | Problem | Improved |
|----------|---------|----------|
| `a(...)` | What does "a" mean? Add? Authenticate? | `registerUser(...)` |
| `f(...)` | What does "f" mean? Find? Fetch? | `findByUsername(...)` |
| `getUn()` | Returns username? Unknown? | `getUsername()` |
| `getPw()` | Returns password? | `getPassword()` |
| `getEm()` | Returns email? EMail? | `getEmail()` |

### 3. Variable naming — abbreviations and snake_case in Java

| Original | Improved | Reason |
|----------|----------|--------|
| `u_list` | `userList` | Snake_case is not idiomatic in Java |
| `nu` | `newUser` | "nu" looks like a typo for "new" |
| `res` | `success` or `result` | "res" is ambiguous |
| `d` | `connection` or `databaseConnection` | Single-letter params are unclear |
| `un` | `username` | Cryptic abbreviation |
| `pw` | `password` | common but ambiguous |
| `em` | `email` | Unclear |

### 4. SQL injection vulnerability

The original builds SQL with string concatenation:
```java
db.execute("INSERT INTO users VALUES ('" + un + "', '" + pw + "', '" + em + "')");
```

If a user registers with username `admin' --`, the query becomes:
```sql
INSERT INTO users VALUES ('admin' --', '...', '...')
```

This deletes the password and email columns from the insert. The AI suggested using **parameterized queries**:
```java
db.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", username, password, email);
```

### 5. Plain-text password storage

The code stores the password in plain text (`pw` field, passed directly to DB). The AI flagged that passwords should be hashed before storage.

### 6. Validation is too weak

- Username minimum is 3 chars but has no maximum
- Password minimum is 8 chars but no complexity requirement (uppercase, number, special char)
- Email check is just `contains("@")` — `"@"` would pass, `"user@@"` would pass

### 7. Missing `@Override` annotations and visibility modifiers

The AI noticed the code is missing standard Java annotations and that internal methods should be `private`.

## Refactored version

```java
public class UserManager {
    private final List<User> userList;
    private final DatabaseConnection connection;

    public UserManager(DatabaseConnection connection) {
        this.connection = connection;
        this.userList = new ArrayList<>();
    }

    public boolean registerUser(String username, String password, String email) {
        if (!isValidUsername(username) || !isValidPassword(password) || !isValidEmail(email)) {
            return false;
        }

        if (findByUsername(username) != null) {
            return false;
        }

        User newUser = new User(username, password, email);
        userList.add(newUser);

        return connection.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            username, password, email
        );
    }

    public User findByUsername(String username) {
        for (User user : userList) {
            if (user.getUsername().equals(username)) {
                return user;
            }
        }
        return null;
    }

    private boolean isValidUsername(String username) {
        return username != null && username.length() >= 3 && username.length() <= 30;
    }

    private boolean isValidPassword(String password) {
        return password != null && password.length() >= 8;
    }

    private boolean isValidEmail(String email) {
        return email != null && email.matches("^[^@]+@[^@]+\\.[^@]+$");
    }
}

public class User {
    private final String username;
    private final String password;
    private final String email;

    public User(String username, String password, String email) {
        this.username = username;
        this.password = password;
        this.email = email;
    }

    public String getUsername() { return username; }
    public String getPassword() { return password; }
    public String getEmail() { return email; }
}
```

## What I might have missed

- **SQL injection**: I noticed the string concatenation, but the severity was easy to underestimate — this is a critical vulnerability
- **Plain-text passwords**: I might have focused on the code structure and forgotten about the security implications of storing passwords without hashing
- **Weak validation**: The `contains("@")` check looks sufficient at a glance, but it's trivially bypassed
- **Missing `final` modifiers**: Not a bug, but makes the code safer and more readable

## Changes I disagree with

The AI suggested extracting a `UserValidator` class with static validation methods. For a simple class like this, that feels like over-engineering — keeping validation as private methods in `UserManager` is cleaner for a small codebase. I'd reserve a separate validator for when validation logic needs to be reused across multiple classes.
