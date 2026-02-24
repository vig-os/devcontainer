workspace {

    model {
        signal = softwareSystem "Signal" "Idea, problem, feedback, or research finding" "trigger"

        group "Inception Phase" {
            explore   = softwareSystem "inception:explore"   "Diverge — understand the problem space"
            scope     = softwareSystem "inception:scope"     "Converge — define what to build"
            architect = softwareSystem "inception:architect"  "Evaluate — validate against patterns"
            plan      = softwareSystem "inception:plan"      "Decompose — break into GitHub issues"
        }

        group "Development Phase" {
            brainstorm = softwareSystem "design:brainstorm"  "Implementation design per issue"
            issue      = softwareSystem "issue:*"            "Issue triage, claiming, creation"
            design     = softwareSystem "design:*"           "Brainstorm and plan implementation"
            code       = softwareSystem "code:*"             "TDD, debug, execute, review, verify"
        }

        group "Delivery Phase" {
            git = softwareSystem "git:*" "Commit workflow"
            ci  = softwareSystem "ci:*"  "Pipeline check and fix"
            pr  = softwareSystem "pr:*"  "Pull request creation and post-merge"
        }

        signal -> explore "triggers"
        explore -> scope "feeds"
        scope -> architect "feeds"
        architect -> plan "feeds"
        plan -> brainstorm "hands off"
        brainstorm -> issue "creates"
        issue -> design "begins"
        design -> code "implements"
        code -> git "commits"
        git -> ci "triggers"
        ci -> pr "delivers"
    }

    views {
        systemLandscape "SkillPipeline" "Full agent-driven development pipeline" {
            include *
            autoLayout lr
        }

        theme default
    }

}
