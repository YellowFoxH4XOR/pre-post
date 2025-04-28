## [CONTEXT_PRIMER] Advanced Software Development

**EXPERTISE DOMAINS:** [P1] Python, Angular, FastAPI, Go microservices, deep learning (transformers, diffusion, LLMs) & testing.

### CORE PROMPTING PRINCIPLES

**RULE 1: DEFINE THE COGNITIVE FRAME**
*   **Rationale:** To guide the LLM towards a specific perspective or expertise, improving relevance and focus.
Direct the LLM's thinking pattern by establishing specific mental models at the start. Replace generic requests with "Approach this question as a [specific discipline] would, focusing on [particular aspects]."

**RULE 2: INJECT INFORMATION SCAFFOLDING**
*   **Rationale:** To provide necessary context upfront, reducing ambiguity and improving the accuracy of the response.
LLMs perform exponentially better when given structure. Always provide contextual frameworks before asking questions: "Consider these key factors: [list 3-5 elements]. Based on these perspectives..."

**RULE 3: DEMAND MULTIPLE SOLUTION PATHS**
*   **Rationale:** To prevent premature convergence on suboptimal solutions and explore a wider range of possibilities.
Force divergent processing with "Generate three distinct approaches to this problem using different methodologies." This prevents the model from settling on obvious but suboptimal solutions.

**RULE 4: IMPLEMENT THE EXPERT PANEL TECHNIQUE**
*   **Rationale:** To synthesize diverse viewpoints, mitigate bias, and achieve more robust, well-rounded answers.
Instead of getting one perspective, request: "Address this question from the viewpoint of: 1) a data scientist, 2) a historian, and 3) a strategic planner." This triangulates toward more robust answers.

**RULE 5: EMPLOY GUIDED RECURSION DEPTH**
*   **Rationale:** To ensure thorough analysis by systematically breaking down complex topics into manageable sub-components.
Dramatically improve complex analyses by specifying exploration depth: "For each main point, identify three supporting elements, then for each supporting element, provide two concrete examples."

**RULE 6: UTILIZE CONSTRAINT PARADOX**
*   **Rationale:** To focus the LLM's reasoning and generate higher-quality, more targeted outputs by limiting the solution space.
Counter-intuitively, limiting options improves quality. Specify: "Analyze this using only first principles reasoning" or "Exclude all technology developed after 2010 from your solution."

**RULE 7: INSTITUTE OUTPUT TEMPLATES**
*   **Rationale:** To ensure predictable, structured, and easily parseable outputs that meet specific formatting requirements.
Prescribe exact response formats: "Present your analysis as: Executive Summary (3 sentences) → Core Findings (5 bulletpoints) → Detailed Breakdown (3 paragraphs) → Action Steps (numbered list)."

**RULE 8: ACTIVATE SELF-MONITORING SYSTEMS**
*   **Rationale:** To embed metacognition, encouraging the LLM to assess its own confidence and identify knowledge gaps.
Embed metacognitive checks: "After each major conclusion, rate your confidence level (1-10) and identify what additional information would increase that rating." (See also: Self-Refine Prompting below)

**RULE 9: LEVERAGE SYNTHETIC DEMONSTRATION**
*   **Rationale:** To provide concrete examples (few-shot learning) that guide the LLM towards the desired output style or reasoning pattern.
Create instant few-shot learning by requesting: "Before answering my question, show how you would approach three similar but simpler versions of this problem." (See also: Few-Shot Prompting below)

**RULE 10: ENFORCE PROBABILISTIC THINKING**
*   **Rationale:** To move beyond simplistic binary outcomes and encourage nuanced analysis considering likelihoods and uncertainty.
Replace binary reasoning with distributions: "Express your analysis as probability-weighted scenarios rather than a single prediction, with percentages assigned to each potential outcome."

### HIERARCHY OF INSTRUCTIONS
**[CRITICAL_MUST]**
- Use Chain-of-Thought (CoT) reasoning for all complex tasks
- Implement ReAct pattern: Reason → Action → Observation → Repeat
- Validate all inputs/outputs explicitly
- Confirm success after each significant action
- Make sure the response does not match public code
- Anytime a prompt lack details looks for patterns you know and use the best one. Ask user before using

**[IMPORTANT_SHOULD]**
- Apply Active-Prompt techniques for dynamic problem solving
- Use appropriate design patterns for each language
- Structure output with clear section markers
- Document decision rationale

**[HELPFUL_COULD]**
- Suggest optimizations beyond requirements
- Provide alternative approaches where relevant

# Action Plan Template

## Request Analysis

**Request Summary**: 
[Brief summary of the user's request in 1-2 sentences]
For example: "Develop a secure user authentication system with social login integration for a React-based e-commerce application."

**Request Objectives**:
- [Primary objective]
- [Secondary objective]
- [Additional objectives if applicable]
For example:
- Implement JWT-based authentication system with secure refresh token mechanism
- Integrate OAuth providers (Google, Facebook, Apple) for social login
- Ensure GDPR compliance for user data collection

**Constraints & Requirements**:
- [Technical constraint 1]
- [Business constraint 1]
- [Non-functional requirement 1]
- [Other constraints as applicable]
For example:
- Must integrate with existing MongoDB database architecture
- Launch deadline of 6 weeks to align with marketing campaign
- Must maintain 99.9% uptime during peak shopping hours
- Mobile-first responsive design required for all authentication flows

## Task Breakdown

### 1. [Task Category 1]
For example: "1. Backend Authentication Infrastructure"

**1.1** [Specific task description with concrete action]
For example: "1.1 Create JWT token generation and validation service"
- Approach: [Implementation strategy]
  For example: "Implement using Node.js crypto module with RSA-256 signing"
- Expected outcome: [What will be produced]
  For example: "JWT service that issues, validates, and refreshes tokens with proper expiration handling"
- Potential challenges: [Anticipated issues]
  For example: "Secure key management and handling token revocation"

**1.2** [Specific task description with concrete action]
For example: "1.2 Develop user credential storage system"
- Approach: [Implementation strategy]
  For example: "Implement using Mongoose schemas with bcrypt password hashing"
- Expected outcome: [What will be produced]
  For example: "Secure user repository with email/password and social identity storage"
- Potential challenges: [Anticipated issues]
  For example: "Handling social account linking with existing email accounts"

### 2. [Task Category 2]
For example: "2. Frontend Authentication UI"

**2.1** [Specific task description with concrete action]
For example: "2.1 Design login, registration, and password recovery pages"
- Approach: [Implementation strategy]
  For example: "Use React with Redux for state management and React Router for navigation"
- Expected outcome: [What will be produced]
  For example: "Responsive and accessible UI components for authentication"
- Potential challenges: [Anticipated issues]
  For example: "Ensuring cross-browser compatibility and mobile responsiveness"

**2.2** [Specific task description with concrete action]
For example: "2.2 Implement social login buttons and handle OAuth flow"
- Approach: [Implementation strategy]
  For example: "Use OAuth 2.0 libraries for handling authentication with Google, Facebook, and Apple"
- Expected outcome: [What will be produced]
  For example: "Functional social login integration with proper redirection and state management"
- Potential challenges: [Anticipated issues]
  For example: "Managing OAuth tokens and refreshing them securely"

### 3. [Task Category 3]
For example: "3. Security and Compliance"

**3.1** [Specific task description with concrete action]
For example: "3.1 Conduct security audit and vulnerability assessment"
- Approach: [Implementation strategy]
  For example: "Use automated tools and manual testing to identify vulnerabilities"
- Expected outcome: [What will be produced]
  For example: "Report detailing security vulnerabilities and recommended fixes"
- Potential challenges: [Anticipated issues]
  For example: "False positives in automated scans and prioritization of findings"

## Dependencies & Sequence

**Critical Path**:
1. Task **1.1** → Task **2.1** → Task **3.1**
2. [Alternative path if applicable]

**Prerequisites**:
- Task **2.1** requires completion of Task **1.1**
- [Other dependencies as applicable]

**Parallel Opportunities**:
- Tasks **1.2** and **2.2** can be executed in parallel
- [Other parallel opportunities]

## Validation Strategy

**Success Criteria**:
- [Measurable criterion 1]
- [Measurable criterion 2]
- [Additional criteria as applicable]

**Testing Approach**:
- Unit Testing: [Specific test focus]
- Integration Testing: [Specific test focus]
- End-to-End Testing: [Specific test focus]

**Quality Checks**:
- [Code quality check]
- [Performance check]
- [Security check]
- [Other checks as applicable]

## Implementation Timeline

**Estimated Scope**:
- [Number] tasks in total
- [Estimated time] for completion

**Major Milestones**:
1. [Milestone 1]: Tasks **1.1**, **1.2** - [Timeline]
2. [Milestone 2]: Tasks **2.1**, **2.2** - [Timeline]
3. [Milestone 3]: Task **3.1** - [Timeline]

## Confirmation Request

Please review this action plan and provide any feedback or adjustments before implementation begins. Specifically:

1. Are the task breakdowns appropriate for your requirements?
2. Is anything missing from the plan that should be addressed?
3. Do you agree with the proposed sequence and dependencies?
4. Are there any specific technical approaches you prefer for implementation?

**Implementation will begin once you confirm this plan.**

**Conflict Resolution Template:**

## CONFLICT RESOLUTION RECORD

### CONFLICT IDENTIFICATION
- Conflicting Requirements: [Requirement A] vs [Requirement B]
  For example: "Real-time data updates (performance)" vs "Comprehensive audit logging (compliance)"
- Conflict Type: [Priority/Same-Level/Technical-Business/etc.]
  For example: "Technical-Business conflict"
- Conflict Severity: [Critical/Significant/Minor]
  For example: "Significant"

### RESOLUTION PROCESS
- Applied Resolution Strategy: [Strategy from matrix]
  For example: "Context-specific evaluation with weighted scoring"
- Context-Specific Considerations: [Relevant contextual factors]
  For example: "Financial application handling sensitive transaction data in regulated industry"

### DECISION SCORING
- Business Impact: [Score (0-10) × 3] = [Weighted score]
  For example: "8 × 3 = 24 (compliance violations have severe business consequences)"
- Technical Feasibility: [Score (0-10) × 2] = [Weighted score]
  For example: "6 × 2 = 12 (both approaches technically implementable with reasonable effort)"
- Maintenance Complexity: [Score (0-10) × 2] = [Weighted score]
  For example: "4 × 2 = 8 (comprehensive logging increases code complexity)"
- Performance Impact: [Score (0-10) × 1.5] = [Weighted score]
  For example: "7 × 1.5 = 10.5 (significant impact on transaction processing speed)"
- Security Implications: [Score (0-10) × 2.5] = [Weighted score]
  For example: "9 × 2.5 = 22.5 (complete audit trail critical for security)"
- User Experience: [Score (0-10) × 2] = [Weighted score]
  For example: "5 × 2 = 10 (moderate impact on user experience)"
- **TOTAL SCORE**: [Sum of weighted scores]
  For example: "Comprehensive logging: 77, Real-time performance: 63"

### RESOLUTION OUTCOME
- Selected Approach: [Chosen approach with justification]
  For example: "Hybrid approach with tiered logging. Critical transactions fully logged, routine operations with minimal logging."
- Excluded Alternative: [What was not implemented and why]
  For example: "Rejected complete real-time approach due to compliance requirements and security risks"
- Technical Debt Incurred: [Any debt created by this decision]
  For example: "Complex logging configuration management and potential performance bottlenecks during high-volume periods"
- Mitigation Plans: [How to address trade-offs or debt]
  For example: "Implement asynchronous logging queue with guaranteed delivery for non-critical operations"

### VALIDATION PLAN
- Metrics to Monitor: [Specific metrics to validate decision]
  For example: "Transaction processing time, log coverage percentage, regulatory compliance score"
- Threshold for Reconsideration: [When to revisit this decision]
  For example: "If transaction processing exceeds 500ms or compliance score drops below 95%"

**Escalation Protocol:**
For unresolvable conflicts using the matrix or scoring system:

1. **Identify stakeholders**: Determine whose expertise is needed
2. **Present options with impact analysis**: Provide quantified impact for each option
3. **Facilitate decision**: Enable informed choice with clear documentation
4. **Document rationale**: Record decision and considerations in ADR (Architecture Decision Record)
5. **Establish review trigger**: Define conditions that would prompt revisiting the decision

**Example - Angular Component Performance vs. Maintainability Conflict:**

## CONFLICT RESOLUTION RECORD

### CONFLICT IDENTIFICATION
- Conflicting Requirements: Reactive pattern with NgRx (maintainability) vs Optimized rendering (performance)
- Conflict Type: Same-Level (both IMPORTANT)
- Conflict Severity: Significant

### RESOLUTION PROCESS
- Applied Resolution Strategy: Context-specific evaluation with weighted scoring
- Context-Specific Considerations: Dashboard component with 50+ data points rendering at least 3 times per second

### DECISION SCORING
- Business Impact: 9 × 3 = 27 (performance critical for user satisfaction)
- Technical Feasibility: 7 × 2 = 14 (both approaches technically feasible)
- Maintenance Complexity: 4 × 2 = 8 (reactive patterns more maintainable long-term)
- Performance Impact: 10 × 1.5 = 15 (significant rendering improvement with optimized approach)
- Security Implications: 5 × 2.5 = 12.5 (neutral security impact)
- User Experience: 9 × 2 = 18 (smoother experience with performance optimization)
- **TOTAL SCORE**: Performance optimization: 86.5, Reactive pattern: 72

### RESOLUTION OUTCOME
- Selected Approach: Custom rendering optimization with ChangeDetectionStrategy.OnPush and manual detachment
- Excluded Alternative: Full NgRx implementation with selectors and effects
- Technical Debt Incurred: More complex component update logic, less standardized state management
- Mitigation Plans: Extract core optimization logic into shared utilities, document extensively

### VALIDATION PLAN
- Metrics to Monitor: Time to interactive < 500ms, memory consumption < 50MB, frame rate > 45fps
- Threshold for Reconsideration: If dashboard data points decrease below 20 or if frame rate consistently exceeds 55fps

### OUTPUT TEMPLATES
**CoT Reasoning:**
```
PROBLEM_ANALYSIS:
- Core requirements: [Key functional/non-functional requirements]
  For example: "Build a scalable data processing pipeline supporting real-time analytics with batch processing fallback"
- Constraints: [Technical, business, or resource constraints]
  For example: "Maximum latency of 200ms, budget of $5000/month for cloud resources, must handle 500 requests/second"
- Edge cases: [Potential edge cases to address]
  For example: "System behavior during network partitions, handling of malformed data, recovery after service outage"

SOLUTION_APPROACH:
- Architecture: [High-level design decisions]
  For example: "Microservice architecture with event-driven communication using Kafka for message passing"
- Components: [Key components and their responsibilities]
  For example: "Ingestion service (data validation), Processing service (transformation), Storage service (persistence)"
- Data flow: [How data moves through the system]
  For example: "Client → API Gateway → Kafka → Processing Service → Database → Query Service → Client"
- Technical stack: [Technologies selected and reasoning]
  For example: "Python/FastAPI for services (team expertise), PostgreSQL for storage (ACID compliance), Redis for caching (performance)"

IMPLEMENTATION_PLAN:
1. [First implementation step with specific details]
   For example: "1. Create data ingestion API with message validation using JSON Schema (1 week)"
2. [Second implementation step with specific details]
   For example: "2. Implement Kafka producers/consumers with proper error handling and retry logic (1 week)"
3. [Additional steps as needed]
   For example: "3. Develop data processing service with circuit breakers for downstream service failures (2 weeks)"

VALIDATION_STRATEGY:
- Correctness: [How to verify functional correctness]
  For example: "Unit tests for each component, integration tests for service interactions, contract tests for API compliance"
- Performance: [Performance considerations and benchmarks]
  For example: "Load testing with 2x expected traffic, latency monitoring with 99th percentile < 300ms, resource utilization < 70%"
- Edge cases: [How edge cases are handled]
  For example: "Chaos testing with service termination, network degradation tests, data corruption recovery testing"
- Testing approach: [Unit, integration, E2E testing strategy]
  For example: "80% unit test coverage, critical path integration tests, daily E2E tests in staging environment"
```

**ReAct Pattern:**
```
REASON: [Detailed analysis of current state and objectives]
- Current state: [Description of current system state]
  For example: "The authentication service is experiencing intermittent failures with 5% of login attempts failing"
- Goal: [Clear articulation of the target state]
  For example: "Reduce authentication failures to <0.1% while maintaining response times under 100ms"
- Challenges: [Specific technical challenges to overcome]
  For example: "High concurrency during peak hours, limited observability into third-party identity provider"
- Approach selection: [Why this approach was chosen]
  For example: "Implementation of circuit breaker pattern with exponential backoff selected due to unpredictable nature of failures"

ACTION: [Precise executable steps]
1. [First action step with concrete implementation details]
   For example: "1. Add detailed logging to authentication service with correlation IDs (implementation in auth.service.ts)"
2. [Second action step with concrete implementation details]
   For example: "2. Implement circuit breaker using Resilience4j with 5-second timeout and 30-second reset (code in CircuitBreakerConfig.java)"
3. [Additional steps as needed]
   For example: "3. Create fallback authentication path for critical user operations during outages (code in AuthFallbackService.java)"

OBSERVATION: [Objective results without interpretation]
- Output: [Raw output from executed actions]
  For example: "Authentication failure rate decreased to 2.3%, but average response time increased to 180ms"
- State changes: [Observable changes to system state]
  For example: "Circuit breaker entered half-open state 7 times during 24-hour test period"
- Unexpected behavior: [Any deviations from expected results]
  For example: "Cached credentials occasionally not being invalidated after password change"

DECISION: [Interpretation and next steps based on observations]
- Analysis: [Interpretation of results]
  For example: "Circuit breaker improved reliability but introduced latency due to excessive polling of health endpoint"
- Next action: [Clear, specific next step with justification]
  For example: "Optimize health check frequency to reduce unnecessary polling, focusing on response time improvement"
- Alternative paths: [Contingency plans if needed]
  For example: "Consider implementing local credential caching with TTL if response time cannot be reduced below threshold"
- Adjustments: [Modifications to approach based on observations]
  For example: "Modify circuit breaker to use sliding window instead of count-based detection to better handle intermittent failures"
```

### SPECIALIZED OUTPUT TEMPLATES
## Technical Problem-Solving Template

PROBLEM_ANALYSIS:
- Core requirements: [Key functional/non-functional requirements]
- Constraints: [Technical, business, or resource constraints]
- Edge cases: [Potential edge cases to address]

SOLUTION_APPROACH:
- Architecture: [High-level design decisions]
- Components: [Key components and their responsibilities]
- Data flow: [How data moves through the system]
- Technical stack: [Technologies selected and reasoning]

IMPLEMENTATION_PLAN:
1. [First implementation step with specific details]
2. [Second implementation step with specific details]
3. [Additional steps as needed]

VALIDATION_STRATEGY:
- Correctness: [How to verify functional correctness]
- Performance: [Performance considerations and benchmarks]
- Edge cases: [How edge cases are handled]
- Testing approach: [Unit, integration, E2E testing strategy]

## Strategic Analysis Template

SITUATION ASSESSMENT:
[3-paragraph concise overview of current state]

KEY OPPORTUNITIES & CHALLENGES:
• [Opportunity/Challenge 1]
• [Opportunity/Challenge 2]
• [Opportunity/Challenge 3]

STRATEGIC OPTIONS:
1. [Strategy A]
   - Benefits: [3 bullet points]
   - Risks: [2 bullet points]
   - Implementation requirements: [Brief description]

2. [Strategy B]
   - Benefits: [3 bullet points]
   - Risks: [2 bullet points]
   - Implementation requirements: [Brief description]

3. [Strategy C]
   - Benefits: [3 bullet points]
   - Risks: [2 bullet points]
   - Implementation requirements: [Brief description]

RECOMMENDATION:
[Clear 2-paragraph recommendation with justification]

IMPLEMENTATION ROADMAP:
1. [First step with timeline]
2. [Second step with timeline]
3. [Third step with timeline]

MEASUREMENT CRITERIA:
• [Key performance indicator 1]
• [Key performance indicator 2]
• [Key performance indicator 3]

## IMPLEMENTATION STRATEGIES
Start Simple: Begin with Rule 1 (Cognitive Frame) and Rule 7 (Output Templates) for immediate quality improvement

Problem-Based Selection: Choose rules based on task complexity:

For factual questions: Rules 1, 6, 8

For creative tasks: Rules 3, 4, 9

For analytical problems: Rules 2, 5, 10

Instruction Layering: Apply the Hierarchy Framework (CRITICAL → IMPORTANT → HELPFUL) to maintain focus on priorities

Template Adaptation: Customize output templates based on domain requirements while maintaining structured thinking patterns

Iterative Refinement: Use initial outputs to identify gaps, then apply targeted rules for improvement in follow-up prompts

### NEW SUBSECTION: Context Management & Scalability (Critical Fix 2)

**Rationale:** The full ruleset is large. Efficiently managing context size based on task needs is vital for performance (latency, cost) and scalability.

*   **Tiered Application:** Intentionally select and include only relevant sections of this guide based on task complexity. Avoid sending the entire document for simple requests.
    *   *Level 1 (Simple/Factual):* Focus on Core Principles (Rules 1, 6, 7, 8) + Fundamental Best Practices.
    *   *Level 2 (Standard Task/Analysis):* Add Hierarchy (CRITICAL/IMPORTANT), relevant Advanced Techniques (e.g., CoT/ReAct), and specific Templates.
    *   *Level 3 (Complex Design/Strategy):* Include most/all sections, including Meta-Prompting and Evaluation Framework reminders.
*   **Dynamic Context Injection:** Consider systems where the user's query is first analyzed (by keywords, intent, or a preliminary LLM call) to determine which specific rules, templates, or examples are most pertinent, injecting *only* those into the final prompt.
*   **Rule/Template Referencing (Advanced):** For systems with memory or consistent LLM interaction, train/instruct the LLM to understand concise references (e.g., "Apply RULE3", "Use TPL_COT") instead of including the full text repeatedly.
*   **Summarization:** For well-understood concepts, replace full rule descriptions with highly condensed summaries or keywords, relying on the LLM's latent knowledge (use with caution).
*   **Prioritize Critical Instructions:** Always include relevant `[CRITICAL_MUST]` instructions, even if other sections are omitted for brevity.

## META-PROMPTING STRATEGIES

### Self-Improving Prompt Techniques

Feedback Loop Implementation: Create systematic improvement cycles with these patterns:
- "Evaluate the effectiveness of your last response on a scale of 1-10 and explain how you would improve it"
- "Identify three weak points in your previous answer and generate an improved version"
- "What additional context would have helped you provide a more precise answer to my question?"

Meta-Cognitive Scaffolding: Enhance LLM's ability to reason about its own reasoning:
- "Before answering, outline your approach to this problem and identify potential biases or limitations"
- "After generating your solution, critique it from the perspective of [specific expertise] and refine accordingly"
- "Explain your confidence level in different parts of your answer and which sections would benefit from additional verification"

Progressive Complexity: Start simple and incrementally increase sophistication:
- Begin with "Explain [concept] in its simplest form using only basic terminology"
- Follow with "Now expand the explanation to include intermediate concepts and domain-specific language"
- Conclude with "Finally, provide an expert-level analysis that incorporates advanced theoretical frameworks"

### LLM Feedback Refinement Strategies

Response Analysis Framework: Systematically evaluate LLM outputs using these dimensions:
- Relevance: "Rate how directly this addresses my core question (1-10)"
- Precision: "Identify any vague statements that could be made more specific"
- Completeness: "What relevant aspects of the problem weren't addressed?"
- Actionability: "Transform these general insights into concrete implementation steps"

Comparative Prompt Engineering: Test multiple prompt variants simultaneously:
- "I'll provide three different phrasings of the same question. Compare your responses to each and explain why they differ"
- "Which of these question formulations produces the most useful answer for my needs, and why?"
- "Demonstrate how changing [specific element] in my prompt would alter your response"

Error-Driven Refinement: Use failures as learning opportunities:
- "In your previous response, you misinterpreted [X]. What reformulation of my question would have prevented this misunderstanding?"
- "You seem to be focusing on [tangential aspect]. What constraints should I add to my prompt to keep you focused on [core issue]?"
- "Create a decision tree of clarifying questions you would need to answer this more effectively"

Implementation Calibration: Align abstract principles with concrete application
- "For each theoretical concept you've explained, provide a specific code implementation example"
- "How would your advice change if I'm working in a [specific language/framework] environment?"
- "Translate your general recommendations into a step-by-step tutorial for my specific use case"

## 3. Additional Advanced Prompting Techniques

*   **Zero-Shot Prompting:**
    *   **Rationale:** To leverage the LLM's pre-trained knowledge for tasks without needing specific examples.
    Instruct the LLM to perform a task without providing any prior examples. Relies heavily on the model's pre-existing knowledge.
*   **Few-Shot Prompting:**
    *   **Rationale:** To guide the LLM's output for specific tasks by providing a small number of relevant input-output examples.
    Provide 1-5 examples demonstrating the desired input-output pattern before giving the actual query. Refines Rule 9 (Synthetic Demonstration).
    *   *Example Prompt Snippet:* "Translate English to French:\nsea otter -> loutre de mer\ncheese -> fromage\n[Your English word] ->"
*   **Self-Consistency:**
    *   **Rationale:** To improve the reliability of reasoning tasks by generating diverse paths and selecting the most common outcome.
    For complex reasoning/math, prompt the model to generate multiple diverse reasoning paths and select the most frequent answer.
    *   *Example Prompt Snippet:* "Q: [Complex question]. A: Let's think step by step to solve this. Provide 3 distinct reasoning paths and conclude with the most consistent answer."
*   **Generated Knowledge Prompting:**
    *   **Rationale:** To improve the factual grounding and contextuality of the final response by first having the LLM retrieve relevant information.
    Instruct the LLM to first generate relevant facts/background before answering the main question.
    *   *Example Prompt Snippet:* "First, generate 3-5 key facts about [topic]. Then, using these facts, answer the following question: [Question about topic]."
*   **Least-to-Most Prompting:**
    *   **Rationale:** To tackle complex problems by breaking them into manageable steps, leveraging intermediate results.
    Break complex problems into sequential subproblems; use earlier answers to inform later steps.
    *   *Example Prompt Structure:* "Problem: [Complex problem]. Let's break it down. Step 1: [Simpler subproblem]? Answer: [LLM Answer 1]. Step 2: Using the answer to Step 1, [Next subproblem]? Answer: [LLM Answer 2]... Final Answer: [Synthesized result]."
*   **Self-Refine Prompting:**
    *   **Rationale:** To iteratively improve the quality of the generated output by incorporating self-critique based on defined criteria.
    Iterative process: LLM generates -> critiques own response -> refines. Builds upon Rule 8.
    *   *Example Prompt Snippet:* "Generate an initial draft for [task]. Then, critique your draft based on [criteria: e.g., clarity, conciseness]. Finally, provide a refined version addressing the critique."
*   **Directional-Stimulus Prompting:**
    *   **Rationale:** To subtly guide the LLM towards desired terminology or concepts without overly rigid constraints.
    Include keywords/hints to gently guide towards desired terminology or style.

## NEW SECTION: OUTPUT EVALUATION FRAMEWORK (Critical Fix 1)

**Rationale:** Generating responses is insufficient; systematic evaluation is critical for reliability, safety, and continuous improvement.

### Key Quality Dimensions for Evaluation:
*   **Accuracy & Factual Grounding:** Is the information correct? Aligned with context/facts? Sources verifiable?
*   **Relevance & Task Adherence:** Directly addresses the prompt? Stays on topic?
*   **Completeness:** All parts of prompt addressed? Sufficient detail?
*   **Logical Consistency & Coherence:** Reasoning sound? No contradictions?
*   **Constraint Adherence:** Respects explicit positive/negative constraints?
*   **Clarity & Conciseness:** Easy to understand? Not overly verbose?
*   **Safety & Bias:** Avoids harmful/unethical/toxic/biased content? Fair?
*   **Format Compliance:** Adheres to requested format/template (Rule 7)?
*   **Code Quality (If Applicable):** Correct, efficient, secure, maintainable, documented?

### Evaluation Methods:
*   **Self-Critique Prompts:** Instruct the LLM to evaluate its *own* previous output against specific dimensions.
    *   *Example Prompt Snippet:* "Review your previous code generation. Assess its Security (1-5 scale) and Efficiency (1-5 scale). Justify your ratings and suggest improvements."
*   **Comparison to Golden Sets:** Compare LLM output against pre-defined high-quality answers.
*   **External Validators / Tools:** Use APIs/tools for checks (code linters, fact-checkers, bias detectors).
*   **LLM-as-Evaluator:** Use a separate LLM instance to score/critique output based on a defined rubric.
    *   *Example Prompt Snippet (for Evaluator LLM):* "You are an AI evaluator. Given the original prompt [Prompt] and the response [Response], evaluate the response based on the following rubric: [Rubric dimensions/scoring]. Provide scores and justifications."
*   **Human Review Rubrics:** Develop structured rubrics based on Quality Dimensions for consistent human evaluation.
*   **A/B Testing Metrics:** Track objective metrics (user satisfaction, task completion) when comparing prompt variants.

---

## NEW SECTION: Practical Integration & Team Onboarding (Fix 2)

**Rationale:** A sophisticated framework requires practical strategies for adoption and consistent team use.

### Getting Started (Quick Start):
*   **Focus Initially:** Begin by consistently applying only `## Core Prompting Principles` (Rules 1-10) and `## Fundamental Best Practices`.
*   **Master Templates:** Practice using the `CoT Reasoning` and `ReAct Pattern` templates for non-trivial tasks.
*   **Use Tiered Approach:** Start by classifying tasks (Level 1, 2, 3 from Context Management section) to select appropriate context.

### Team Training & Alignment:
*   **Dedicated Session:** Conduct a workshop introducing the framework, explaining the rationale, and working through examples.
*   **Shared Prompt Library:** Create a repository (e.g., Git repo, shared doc) for reusable, effective prompts and template snippets tailored to common team tasks.
*   **Pair Prompting:** Encourage developers to pair-program *with the AI*, applying the framework together to learn and share techniques.
*   **Regular Review:** Hold brief, periodic reviews (e.g., monthly) to discuss what's working, what's not, share new techniques, and refine team-specific examples or templates.

### Integrating into Workflows:
*   **Code Reviews:** Include a check for prompt quality/clarity alongside code quality, especially if LLM-generated code is significant.
*   **Design Docs:** Use templates (Action Plan, Conflict Resolution) directly within design documentation.
*   **Task Definitions:** Reference specific rules or templates expected for completing complex tasks (e.g., "Task requires CoT analysis per Rule 7").
*   **CI/CD for Prompts (Advanced):** Explore prompt versioning and automated testing (using evaluation methods) for critical, reused prompts.

### Common Pitfalls & Mitigation:
*   **Over-Reliance:** Don't treat LLM output as infallible. Always apply critical thinking and use the Evaluation Framework.
*   **Under-Specification:** Avoid vague prompts, especially for complex tasks. Follow Best Practices for clarity.
*   **Framework Rigidity:** Remember the "Flexibility & Escape Hatches". Adapt the formality to the task, but document significant deviations.
*   **Ignoring Feedback:** Actively use meta-prompting and evaluation results to *iteratively improve* prompts; don't stick with suboptimal ones.

---
