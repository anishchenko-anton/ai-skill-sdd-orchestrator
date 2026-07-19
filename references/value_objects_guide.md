# Value Objects Implementation Guide

A Value Object is a small object that represents a simple entity whose equality is not based on identity, but on its value. In our engineering standards, **never use raw primitives (strings, numbers)** for domain concepts. Wrap them in self-validating Value Objects.

---

## TypeScript Implementation (Universal for Angular & NestJS)

Use class constructors that validate the input immediately. Once instantiated, the object must be immutable. Since both the Frontend (Angular) and Backend (NestJS) share the TypeScript language, this standard applies universally across the stack.

### Example: Email Value Object
```typescript
export class Email {
  private readonly value: string;

  constructor(email: string) {
    if (!email || !this.isValidEmail(email)) {
      throw new Error(`Invalid email format: ${email}`);
    }
    this.value = email.trim().toLowerCase();
  }

  private isValidEmail(email: string): boolean {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  toString(): string {
    return this.value;
  }

  equals(other: Email): boolean {
    return this.value === other.toString();
  }
}
```

### Example: UserId Value Object
```typescript
export class UserId {
  private readonly value: string;

  constructor(id: string) {
    if (!id || id.trim().length === 0) {
      throw new Error('UserId cannot be empty');
    }
    this.value = id.trim();
  }

  toString(): string {
    return this.value;
  }

  equals(other: UserId): boolean {
    return this.value === other.toString();
  }
}
```

---

## Why Value Objects?

1. **Validation is Centralized**: You cannot instantiate an invalid `Email` or `UserId`. This eliminates buggy database writes in NestJS and front-end rendering crashes in Angular.
2. **Type Safety**: A method like `sendEmail(userId: string, email: string)` can easily be miscalled as `sendEmail(email, userId)`. A typed method `sendEmail(userId: UserId, email: Email)` prevents compilation-time errors across your entire stack.
