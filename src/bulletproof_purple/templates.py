"""Narrative templates for Purple Agent.

Provides template narratives for different R&D scenarios:
- Qualifying: Clear technical uncertainty and experimentation
- Non-qualifying: Routine engineering or vague claims
- Edge case: Borderline scenarios for testing
"""


class NarrativeTemplates:
    """Template library for R&D tax credit narratives."""

    def qualifying(self) -> str:
        """Generate qualifying R&D narrative with clear technical uncertainty.

        Returns:
            Narrative text demonstrating qualifying R&D activities
        """
        return (
            "Our engineering team developed a novel distributed consensus algorithm to achieve "
            "sub-100ms transaction finality in a Byzantine fault-tolerant system. The technical "
            "uncertainty centered on whether we could maintain consistency guarantees while "
            "achieving this latency target across geographically distributed nodes spanning three "
            "continents. No existing solution in published literature had demonstrated this "
            "combination of low latency and strong consistency at our required scale.\n\n"
            "We faced an unknown: existing Raft and Paxos implementations exhibited 300-500ms "
            "latencies due to multiple round trips. Our hypothesis was that a hybrid approach "
            "combining optimistic concurrency with conflict-free replicated data types (CRDTs) "
            "could reduce synchronization overhead by 60-70%. This required fundamental research "
            "into whether CRDTs could be adapted for financial transactions where strong ordering "
            "guarantees are mandatory.\n\n"
            "Our process of experimentation included systematic testing of multiple approaches. "
            "First, we implemented a baseline Raft cluster and measured P99 latencies at 420ms "
            "under realistic load conditions with 50,000 transactions per second. We then tested "
            "three alternative approaches: (1) speculative execution with rollback (failed - 15% "
            "transaction abort rate unacceptable for production use), (2) pipeline optimization "
            "with batching (reduced latency to 280ms but violated linearizability requirements), "
            "and (3) our novel CRDT-based approach with vector clocks and custom conflict "
            "resolution.\n\n"
            "The third approach initially failed validation tests due to clock skew exceeding 50ms "
            "between nodes in different data centers. After implementing NTP synchronization and "
            "hybrid logical clocks, we achieved 85ms P99 latency while maintaining strong "
            "consistency. We documented 12 failed prototypes and 47 performance test iterations "
            "before reaching this solution. Each failure taught us critical constraints about "
            "network behavior and consistency trade-offs.\n\n"
            "The development required 8 months of dedicated research and involved evaluating "
            "alternatives not available in published literature, including custom conflict "
            "resolution strategies and a new leader election protocol optimized for "
            "cross-datacenter scenarios. Our final implementation reduced inter-datacenter "
            "communication rounds from 4 to 2 while maintaining Byzantine fault tolerance. This "
            "represented a fundamental advancement in distributed systems architecture for "
            "financial applications requiring both low latency and strong consistency guarantees. "
            "We filed provisional patents for three novel techniques discovered during this "
            "research process."
        )

    def non_qualifying(self) -> str:
        """Generate non-qualifying narrative with routine engineering.

        Returns:
            Narrative text demonstrating non-qualifying activities
        """
        return (
            "Our team worked on improving the performance of our web application to enhance user "
            "experience. We noticed the application was running slowly, so we decided to optimize "
            "it and make it better. The goal was to improve overall system performance and user "
            "satisfaction through various enhancements.\n\n"
            "We started by debugging various performance issues in the production environment. The "
            "main problems were related to slow database queries and inefficient code. We fixed "
            "several bugs that were causing the application to crash during peak usage times. "
            "These issues were identified through standard monitoring tools and resolved using "
            "established debugging techniques.\n\n"
            "To improve things, we refactored the codebase to follow better coding practices and "
            "upgraded several dependencies to their latest versions. We also performed routine "
            "maintenance tasks like cleaning up unused code and updating documentation. The "
            "database was migrated to a newer version with better performance characteristics. "
            "This migration followed the vendor's documented upgrade path.\n\n"
            "We optimized various API endpoints by adding caching and improving query efficiency. "
            "The overall user experience was enhanced through these improvements. We also did some "
            "code cleanup to make the codebase more maintainable going forward. Standard "
            "optimization patterns like memoization and lazy loading were applied throughout the "
            "application.\n\n"
            "After deploying these changes, we observed that the application performed better and "
            "users reported faster load times. The system was more stable and required less "
            "troubleshooting. We successfully completed the performance tuning project and handed "
            "it off to the operations team for ongoing monitoring and maintenance. The "
            "improvements were achieved through application of well-known best practices.\n\n"
            "Throughout the project, we followed standard engineering practices and applied "
            "well-known optimization techniques. The work primarily involved applying existing "
            "knowledge to improve system performance using established methodologies. All "
            "solutions were based on common industry patterns and vendor recommendations. No novel "
            "approaches or experimental techniques were required, as the problems we encountered "
            "were typical of web applications at this scale."
        )

    def edge_case(self) -> str:
        """Generate edge case narrative with borderline characteristics.

        Returns:
            Narrative text demonstrating borderline R&D scenario
        """
        return (
            "Our team developed a new microservices architecture to improve system scalability and "
            "reduce deployment times. While we followed established patterns, we faced uncertainty "
            "around optimal service granularity for our specific domain model. The project "
            "involved both routine application of known patterns and some areas requiring "
            "experimentation.\n\n"
            "We needed to determine whether to split our monolithic order processing system into "
            "5, 12, or 20+ microservices. The technical challenge was balancing service cohesion "
            "against operational complexity. We hypothesized that domain-driven design bounded "
            "contexts would guide optimal decomposition, but our multi-tenant SaaS model "
            "introduced complications not clearly addressed in existing literature. Multi-tenancy "
            "at our scale created unique challenges around data isolation and performance.\n\n"
            "Our experimentation process involved systematic testing. We started with Martin "
            "Fowler's microservices patterns and implemented a 5-service architecture. Load "
            "testing revealed bottlenecks in the shared payment service processing 40,000 "
            "transactions per hour. We tried two alternatives: (1) vertical scaling the payment "
            "service (hit CPU limits at 55,000 tx/hour), and (2) horizontal partitioning by "
            "tenant (worked but introduced operational complexity around tenant routing).\n\n"
            "Some aspects were straightforward - we applied standard API gateway patterns and used "
            "Kubernetes for orchestration following cloud-native best practices. However, "
            "cross-service transaction coordination proved difficult. We tested three approaches: "
            "saga pattern with event sourcing, two-phase commit, and eventual consistency with "
            "compensating transactions. The first two didn't meet our 99.9% reliability SLA "
            "during stress testing with simulated failures.\n\n"
            "We ultimately implemented a hybrid approach using event sourcing for order state with "
            "compensating workflows for failures. While we built on existing patterns, the "
            "specific combination and tuning for our multi-tenant constraints required significant "
            "experimentation. We documented 8 architectural iterations and conducted 30+ load test "
            "scenarios before achieving our performance targets of 100,000 transactions per hour "
            "with P95 latency under 200ms.\n\n"
            "The project combined routine engineering (applying standard microservices patterns, "
            "using established tools) with areas of genuine uncertainty (multi-tenant transaction "
            "coordination, service boundary optimization). Approximately 60% of the effort "
            "involved straightforward application of known techniques, while 40% required "
            "experimental approaches to solve problems not fully addressed in available "
            "documentation or research."
        )
