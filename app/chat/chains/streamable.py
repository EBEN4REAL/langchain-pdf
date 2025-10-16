from flask import current_app
from queue import Queue
from threading import Thread
from typing import Any, Dict, Iterator, Union
from app.chat.callbacks.stream import StreamingHandler
import time

class StreamableChain:
    """
    Mixin class to add streaming capability to LangChain chains.
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
        result_container = {}  # Store the final result

        def task(app_context):
            app_context.push()
            try:
                print(f"[StreamableChain] Starting chain with input: {input}")
                
                config = {"callbacks": [handler]}
                
                # ConversationalRetrievalChain expects a dict with 'question' key
                if isinstance(input, str):
                    chain_input = {"question": input}
                elif isinstance(input, dict) and "input" in input:
                    chain_input = {"question": input["input"]}
                else:
                    chain_input = input
                
                # Execute the chain
                if hasattr(self, 'invoke'):
                    result = self.invoke(chain_input, config=config)
                else:
                    result = self(chain_input, callbacks=[handler])
                
                print(f"[StreamableChain] Result type: {type(result)}")
                result_container['result'] = result
                
                # Give streaming a moment to catch up
                time.sleep(0.1)
                    
            except Exception as e:
                print(f"[StreamableChain] Error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                queue.put(None)

        thread = Thread(target=task, args=[current_app.app_context()])
        thread.start()
        
        token_count = 0
        received_any_tokens = False
        
        # Yield tokens from queue
        while True:
            token = queue.get()
            if token is None:
                break
            token_count += 1
            received_any_tokens = True
            yield token
        
        # Wait for thread to complete
        thread.join()
        
        # FALLBACK: If no tokens were received but we have a result, yield it
        if not received_any_tokens and 'result' in result_container:
            result = result_container['result']
            if isinstance(result, dict) and 'answer' in result:
                answer = result['answer']
                print(f"[StreamableChain] No tokens received, yielding answer from result: {answer[:100]}...")
                
                # Yield answer word by word to simulate streaming
                words = answer.split(' ')
                for i, word in enumerate(words):
                    if i == 0:
                        yield word
                    else:
                        yield ' ' + word
                    time.sleep(0.01)  # Small delay to simulate streaming
        
        print(f"[StreamableChain] Complete. Yielded {token_count} tokens")