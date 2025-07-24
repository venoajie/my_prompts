<!-- PEL INSTANCE REQUEST: DEPLOYMENT PLAN -->
<!-- SYSTEM CORE: PEL_SYSTEM_CORE_V1.0.prompt -->
<Instance>
    <KnowledgeBase>
        <!-- The DPA-1 persona's protocol requires the blueprint to understand the system -->
        <Document id="ARCHITECTURE_BLUEPRINT" version="2.5" src="PROJECT_BLUEPRINT_V2.5.md" description="The primary architectural blueprint and single source of truth.">
        ```markdown
        <!-- The full, complete text of PROJECT_BLUEPRINT_V2.5.md goes here -->
        ```
        </Document>
        
        <Document id="RAW_DOCKER_COMPOSE" src="docker-compose.yml" description="The Docker Compose configuration defining the system's services.">
        ```yaml
        # The full, complete text of your docker-compose.yml goes here
        ```
        </Document>
    </KnowledgeBase> 
    <SessionState>    
        <last_outcome status="SUCCESS">
            <summary>
            System testing is complete. All known critical bugs have been addressed. The system is now considered a release candidate.
            The next step is to generate a formal plan for the first production deployment.
            </summary>
        </last_outcome>
    </SessionState>
    <Runtime>
        <ActivatePersona alias="DPA-1"/>
        <Mandate>
            Generate a comprehensive production deployment plan for the system defined in the `ARCHITECTURE_BLUEPRINT`.
            The target user is a developer with no prior production deployment experience, so the plan must be explicit, detailed, and prioritize safety and verifiability above all else.
        </Mandate>
    </Runtime>
</Instance>