from flask import current_app
from queue import Queue
from threading import Thread
from typing import Any, Dict, Iterator, Union
from app.chat.callbacks.stream import StreamingHandler

class StreamableChain:
    """
    Mixin class to add streaming capability to LangChain chains.
    
    Usage:
        class MyChain(StreamableChain, RunnableSequence):
            pass
        
        chain = MyChain(...)
        for token in chain.stream({"input": "Hello"}):
            print(token, end="", flush=True)
    """
    
    def stream(self, input: Union[Dict[str, Any], str]) -> Iterator[str]:
        """
        Stream tokens from the chain execution.
        
        Args:
            input: Input to the chain (dict or string)
            
        Yields:
            str: Individual tokens from the LLM response
        """
        queue = Queue()
        handler = StreamingHandler(queue)

        def task(app_context):
            app_context.push()
            try:
                # Handle both invoke and __call__ methods
                if hasattr(self, 'invoke'):
                    self.invoke(input, config={"callbacks": [handler]})
                else:
                    self(input, callbacks=[handler])
            except Exception as e:
                # Ensure queue gets None even on error
                queue.put(None)
                raise e

        thread = Thread(target=task, args=[current_app.app_context()])
        thread.start()
        
        while True:
            token = queue.get()
            if token is None:
                break
            yield token
        
        # Wait for thread to complete
        thread.join()