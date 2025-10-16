
from flask import Blueprint, g, request, Response, jsonify, stream_with_context
from app.web.hooks import login_required, load_model
from app.web.db.models import Pdf, Conversation
from app.chat import build_chat, ChatArgs
from app.web.api import add_message_to_conversation
import json

bp = Blueprint("conversation", __name__, url_prefix="/api/conversations")


@bp.route("/", methods=["GET"])
@login_required
@load_model(Pdf, lambda r: r.args.get("pdf_id"))
def list_conversations(pdf):
    return [c.as_dict() for c in pdf.conversations]


@bp.route("/", methods=["POST"])
@login_required
@load_model(Pdf, lambda r: r.args.get("pdf_id"))
def create_conversation(pdf):
    conversation = Conversation.create(user_id=g.user.id, pdf_id=pdf.id)
    return conversation.as_dict()


@bp.route("/<string:conversation_id>/messages", methods=["POST"])
@login_required
@load_model(Conversation)
def create_message(conversation):
    input_text = request.json.get("input")
    streaming = request.args.get("stream", "false").lower() == "true"

    print(f"\n{'='*60}")
    print(f"[API] New message received")
    print(f"[API] Conversation ID: {conversation.id}")
    print(f"[API] User input: '{input_text}'")
    print(f"[API] Streaming: {streaming}")
    
    pdf = conversation.pdf

    chat_args = ChatArgs(
        conversation_id=conversation.id,
        pdf_id=pdf.id,
        streaming=streaming,
        metadata={
            "conversation_id": conversation.id,
            "user_id": g.user.id,
            "pdf_id": pdf.id,
        },
    )

    chat = build_chat(chat_args)

    # Debug: Check memory state BEFORE running chain
    if hasattr(chat, 'memory'):
        print(f"\n[API] Memory Check - BEFORE execution:")
        if hasattr(chat.memory, 'chat_memory'):
            messages = chat.memory.chat_memory.messages
            print(f"[API]   Total messages in history: {len(messages)}")
            for i, msg in enumerate(messages[-4:]):  # Show last 4
                print(f"[API]   [{i}] {msg.type}: {msg.content[:80]}...")

    if not chat:
        return "Chat not yet implemented!"

    if streaming:
        # We'll collect the full response as it streams
        collected_tokens = []
        
        def generate():
            try:
                print(f"\n[API] Starting stream generation")
                token_count = 0
                
                # Stream the response
                for token in chat.stream(input_text):
                    token_count += 1
                    collected_tokens.append(token)
                    
                    # Debug first few tokens
                    if token_count <= 3:
                        print(f"[API] Token #{token_count}: {repr(token)}")
                    
                    yield f"data: {json.dumps({'token': token})}\n\n"
                
                # Combine all tokens into full response
                full_response = "".join(collected_tokens)
                print(f"\n[API] Stream complete!")
                print(f"[API] Total tokens: {token_count}")
                print(f"[API] Full response length: {len(full_response)} chars")
                print(f"[API] Full response preview: {full_response[:150]}...")
                
                # CRITICAL: Manually save both messages to memory/database
                # This ensures the conversation history is preserved
                try:
                    print(f"\n[API] Saving messages to database...")
                    
                    # Save human message
                    add_message_to_conversation(
                        conversation_id=conversation.id,
                        content=input_text,
                        role="human"
                    )
                    print(f"[API]   ✓ Saved human message")
                    
                    # Save AI response
                    add_message_to_conversation(
                        conversation_id=conversation.id,
                        content=full_response,
                        role="ai"
                    )
                    print(f"[API]   ✓ Saved AI response")
                    
                    # Also save to the chain's memory for immediate use
                    if hasattr(chat, 'memory') and hasattr(chat.memory, 'save_context'):
                        chat.memory.save_context(
                            {"input": input_text},
                            {"answer": full_response}  # Note: use "answer" not "output"
                        )
                        print(f"[API]   ✓ Saved to chain memory")
                    
                except Exception as save_error:
                    print(f"[API] ERROR saving messages: {save_error}")
                    import traceback
                    traceback.print_exc()
                
                yield "data: [DONE]\n\n"
                print(f"{'='*60}\n")
                
            except Exception as e:
                print(f"\n[API] ERROR in stream: {e}")
                import traceback
                traceback.print_exc()
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
            }
        )
    else:
        # Non-streaming path
        result = chat.run(input_text)
        
        # Save messages for non-streaming too
        add_message_to_conversation(
            conversation_id=conversation.id,
            content=input_text,
            role="human"
        )
        add_message_to_conversation(
            conversation_id=conversation.id,
            content=result,
            role="ai"
        )
        
        return jsonify({"role": "assistant", "content": result})
