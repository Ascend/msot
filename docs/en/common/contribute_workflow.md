# Contribution Workflow and Code Style Guide

<br>

Thank you for considering contributing! We welcome all forms of contributions, including bug fixes, feature enhancements, documentation improvements, and even simple usage feedback. 
Whether you are an experienced developer or a newcomer to open source projects, your contribution is highly valued.

You can support this project in the following ways:

- **Code contributions**: Fix known bugs, optimize performance, refactor improvements, or implement new features. Please follow the [Contribution Workflow](#1-contribution-workflow) and [Code Style](#2-code-style) sections below to submit your code.
- **Issue feedback**: Report bugs, suggest features or usage questions via Issues, or participate in requirement reviews and solution discussions.
- **Documentation improvement**: Correct documentation errors, supplement missing content, refine expressions, or write usage examples and tutorials. Please follow the [Documentation Standards](#3-documentation-standards).
- **Quality assurance**: Supplement or improve test cases, review Pull Requests and provide constructive feedback, and assist other contributors in improving code quality.
- **Community promotion**: Answer questions in Issues/PRs, share usage experiences and best practices, or promote the project by writing blogs, tutorials, and through technical communities, social media, and other channels.

## 1. Contribution Workflow

1. **Fork the repository**: Fork the source code repository to your personal repository, then clone your personal repository to your local development environment.
2. **Create a branch**: Create a feature branch based on the latest main branch. The branch name should be concise and reflect the changes (e.g., `fix_xxx_bug`, `feature_xxx`).
3. **Code development**: Develop on the feature branch, follow the [Code Style](#2-code-style), and keep commit records clear and atomic.
4. **Local testing**: Perform thorough functional verification of the code, supplement unit tests as needed based on the developed modules, and ensure all tests pass.
5. **Documentation update**: Supplement or update documentation related to the changes, follow the [Documentation Standards](#3-documentation-standards).
6. **Request Merge**: Submit a PR following the [Pull Request Specification](#4-pull-request-guidelines). For detailed procedures, refer to the [Pull Request Workflow Description](#5-pull-request-workflow-description).
7. **Track Integration**: Monitor the pull request progress, respond to review comments promptly, and modify the code until it passes review and is merged into the main branch.

<br>

## 2. Code Style

### 2.1 Python Code Style

- **Coding standards**: Follow [PEP 8](https://peps.python.org/pep-0008/). It is recommended to use `flake8` or `pylint` for static checking.
- **Style requirements**: A single line of code should not exceed 120 characters. Consider splitting functions longer than 30 lines to improve readability.
- **Comment requirements**: Complex logic and public interfaces must have comments. Modules, classes, and key functions should include docstrings describing their purpose, parameters, and return values.
- **Exception handling**: Handle exceptions properly. Swallowing exceptions without handling or logging them is prohibited. Ensure resource release on critical paths.

### 2.2 C++ Code Style

- **Consistency**: Follow the project's existing coding style and maintain consistency with surrounding code.
- **Naming conventions**: Use PascalCase for class and struct names (e.g., `DataManager`) and camelCase for function names (e.g., `parseData`).
- **Comment requirements**: Complex logic and public interfaces must include comments describing the functionality, parameters, and return values.
- **Exception handling**: Handle exceptions properly; swallowing exceptions without handling or logging is prohibited. Use RAII for resource acquisition to ensure exception safety.

## 3. Documentation Standards

- **Concise expression**: Use clear and concise language, avoid ambiguity and redundancy, and maintain consistent technical terminology.
- **Clear structure**: Use distinct heading levels and logical chapter divisions. Important conclusions or notes may be appropriately highlighted.
- **Complete examples**: Provide complete, runnable example code, specify the runtime environment or dependencies, and include explanations for key steps.
- **Illustrative content**: Complex workflows, configuration items, or interface operations should be accompanied by necessary diagrams to facilitate reader understanding.

## 4. Pull Request Guidelines

- **Moderate size**: A single PR should not be excessively large, making it easier for reviewers to understand and provide quick feedback.
- **Single responsibility**: One PR should only address one issue or implement one feature, facilitating traceability and merging.
- **Timely response**: Respond to or revise based on review comments promptly to avoid blocking the merge workflow.

<br>

## 5. Pull Request Workflow Description

### 5.1 Pre-Submission Checklist

Before submitting a Pull Request, please ensure:

- [ ] The code follows the project's coding standards.
- [ ] Necessary test cases have been added.
- [ ] All tests pass.
- [ ] Updated relevant documentation.
- [ ] Commit message is clear and explicit.
- [ ] Code has been self-reviewed.
  
### 5.2 Creating a PR

When creating a pull request on [GitCode](https://gitcode.com/), please fill in the following completely:

1. **Title**: Briefly summarize the topic or feature of this change.
2. **Description**: Explain what was changed, the reason for the modification, and the self-test status (including environment and results) to facilitate the reviewer's understanding.
3. **Associated issue**: The PR must be associated with an Issue for traceability.

### 5.3 Code Review

1. After submitting the PR, the content will be reviewed by Reviewers and Committers.
2. Revise the code based on review feedback and push updates; multiple iterations may be required. Please respond promptly and maintain communication.

### 5.4 Code Merge

A PR must sequentially obtain the following four labels before it can be merged into the main branch:

| Label | Description                                                         |
|------|------------------------------------------------------------|
| `ascend-cla/yes` | **CLA Signed**: First-time contributors must complete the CLA signing. Subsequent commits will automatically receive this label.                    |
| `ci-pipeline-passed` | **CI Passed**: Comment `compile` in the PR to trigger the pipeline; if it fails, revise according to the prompts and resubmit.         |
| `lgtm` | **Reviewer Approved**: After approval by 2 Reviewers, comment `/lgtm` in the PR to obtain this label.    |
| `approved` | **Committer Approved**: After approval by Committers, comment `/approved` in the PR to obtain this label. |

Once all four labels above are collected, the PR will be merged into the main branch.
