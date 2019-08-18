class AgentCountLogger:
    count = 0

    def bind(logger, agent_class):
        class CountLoggingAgentClass(agent_class):
            def __init__(self, *args):
                super().__init__(*args)

            def initialize(self):
                super().initialize()
                logger.count += 1

            def cleanup(self):
                super().cleanup()
                logger.count -= 1

        return CountLoggingAgentClass
