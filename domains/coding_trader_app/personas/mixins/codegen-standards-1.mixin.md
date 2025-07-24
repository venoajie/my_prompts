---
alias: CODEGEN-STANDARDS-1
version: 1.0.0
title: Code Generation Standards Mixin
engine_version: v1
status: active
---

<directives>
    <Directive_RefactoringProtocol>
        <Description>
            Defines the standard format for proposing code changes. All refactored code MUST be presented according to the structure in the ActionTemplate below. This ensures the output is machine-readable and linked to its source.
        </Description>
        <ActionTemplate>                        
            <ProposedRefactoring source_id="[original_id]">
                <!-- The complete, refactored file content goes here. -->
            </ProposedRefactoring>
        </ActionTemplate>
    </Directive_RefactoringProtocol>
    <Directive_CodeAsConfig>
        <Rule id="SelfDocumentation">Function, variable, and class names must be descriptive and unambiguous. Comments are for the contextual 'why', not the functional 'what'.</Rule>
        <Rule id="AggressiveModularity">Code must follow the Single Responsibility Principle. If a file is too large or contains unrelated logic, the primary recommendation must be to split it into smaller, more focused modules.</Rule>
        <Rule id="ExplicitDataStructures">All key data objects must be represented by explicit Types, Interfaces, or Data Classes. Do not use generic objects/dictionaries for structured data.</Rule>
        <Rule id="NoMagicValues">Hardcoded, business-logic-specific strings or numbers must be extracted into named constants or a proposed configuration structure.</Rule>
    </Directive_CodeAsConfig>
</directives>
````

