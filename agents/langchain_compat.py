try:
    from langchain_core.runnables import RunnableLambda
except ModuleNotFoundError:
    class RunnableLambda:
        def __init__(self, func):
            self.func = func

        def invoke(self, payload):
            return self.func(payload)
