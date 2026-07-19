# Universal TDD and Testing Standards

This document establishes the testing standards for all SDD subagents. Under SDD, **all tests must be written based on the Markdown Specifications, not the final implementation code.**

---

## 1. Test-Driven Development (TDD) Workflow

1. **Red Phase**: Write unit tests for all scenarios described in the module's `.openspec/specs.md`. Since the implementation code doesn't exist yet (or is empty), the tests must fail.
2. **Green Phase**: Write the simplest implementation code to make all unit tests pass.
3. **Refactor Phase**: Clean up the code (ensure SOLID, remove duplication) while keeping the tests green.

---

## 2. Frontend Unit Testing

Always test UI components and state management services in isolation. Use mock classes or spies for external HTTP dependencies. The specific testing library (Jest, Jasmine, Vitest) is determined by the project stack.

### Illustrative Example (Angular / Jest)
```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { UserProfileComponent } from './user-profile.component';
import { UserService } from '../../services/user.service';
import { of } from 'rxjs';

describe('UserProfileComponent', () => {
  let fixture: ComponentFixture<UserProfileComponent>;
  let mockUserService: jest.Mocked<UserService>;

  beforeEach(async () => {
    mockUserService = {
      getProfile: jest.fn().mockReturnValue(of({ username: 'john_doe', bio: 'Hello!' }))
    } as any;

    await TestBed.configureTestingModule({
      imports: [UserProfileComponent],
      providers: [{ provide: UserService, useValue: mockUserService }]
    }).compileComponents();

    fixture = TestBed.createComponent(UserProfileComponent);
    fixture.detectChanges();
  });

  it('should display username from spec on load', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.username')?.textContent).toContain('john_doe');
  });
});
```

---

## 3. Backend Unit Testing

Test backend controllers and services in isolation. Mock database repositories and external APIs. The testing library (Jest, Pytest, Go testing) is determined by the project stack.

### Illustrative Example (NestJS / Jest)
```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { UserService } from './user.service';

describe('UserService', () => {
  let service: UserService;
  let mockRepository = { findOne: jest.fn() };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        UserService,
        { provide: 'UserRepository', useValue: mockRepository },
      ],
    }).compile();

    service = module.get<UserService>(UserService);
  });

  it('should return user profile successfully', async () => {
    mockRepository.findOne.mockResolvedValue({ id: '123', username: 'alice' });
    const profile = await service.getProfile('123');
    expect(profile.username).toEqual('alice');
  });
});
```

---

## 4. Coverage Requirements

- **Branch Coverage Limit**: Branch coverage must be **>= 80%**.
- Check coverage before committing code by running:
  `python .agents/skills/sdd-orchestrator/scripts/run_coverage.py <path_to_report>`
- If coverage is below 80%, identify untested logical branches (e.g. error handling, null inputs) and write specific tests to cover them.
