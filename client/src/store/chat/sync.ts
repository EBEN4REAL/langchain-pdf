import type { Message } from './store';
import { store, set, insertMessageToActive, removeMessageFromActive } from './store';
import { api, getErrorMessage } from '$api';

const _addPendingMessage = (message: Message, pendingId: number) => {
	insertMessageToActive(message);
	insertMessageToActive({
		id: pendingId,
		role: 'pending',
		content: '...'
	});
};


export const sendMessage = async (message: Message, streamData) => {
	set({ loading: true });
	const pendingId = Math.random();
	
	try {
		_addPendingMessage(message, pendingId);

		const conversationId = store.get().activeConversationId;
		
		if (streamData.useStreaming) {
			// Streaming approach
			const streamingMessageId = Math.random();
			let accumulatedContent = '';
			
			// Add placeholder for AI response
			const aiMessage: Message = {
				id: streamingMessageId,
				content: '',
				role: 'ai',
				isStreaming: true, // Add this flag to track streaming state
				timestamp: new Date().toISOString()
			};
			
			removeMessageFromActive(pendingId);
			insertMessageToActive(aiMessage);
			
			try {
				const response = await fetch(
					`/api/conversations/${conversationId}/messages?stream=true`,
					{
						method: 'POST',
						headers: {
							'Content-Type': 'application/json',
						},
						body: JSON.stringify({ input: message.content }),
					}
				);

				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`);
				}

				const reader = response.body?.getReader();
				if (!reader) {
					throw new Error('No reader available');
				}

				const decoder = new TextDecoder();
				let buffer = '';

				while (true) {
					const { done, value } = await reader.read();
					if (done) break;

					buffer += decoder.decode(value, { stream: true });
					const lines = buffer.split('\n');
					
					// Keep the last incomplete line in the buffer
					buffer = lines.pop() || '';

					for (const line of lines) {
						if (line.startsWith('data: ')) {
							const data = line.slice(6).trim();
							
							if (data === '[DONE]') {
								// Mark streaming as complete
								updateMessageInActive(streamingMessageId, {
									...aiMessage,
									content: accumulatedContent,
									isStreaming: false
								});
								set({ loading: false });
								return;
							}

							try {
								const parsed = JSON.parse(data);
								if (parsed.token) {
									accumulatedContent += parsed.token;
									
									// Update the message in real-time
									updateMessageInActive(streamingMessageId, {
										...aiMessage,
										content: accumulatedContent
									});
								}
							} catch (e) {
								console.error('Error parsing token:', e, data);
							}
						}
					}
				}
				
				// Final update
				updateMessageInActive(streamingMessageId, {
					...aiMessage,
					content: accumulatedContent,
					isStreaming: false
				});
				
			} catch (streamError) {
				console.error('Streaming error:', streamError);
				removeMessageFromActive(streamingMessageId);
				throw streamError;
			}
			
		} else {
			// Non-streaming approach (fallback)
			const { data: responseMessage } = await api.post<Message>(
				`/conversations/${conversationId}/messages`,
				{
					input: message.content
				}
			);

			console.log('Response message:', responseMessage);

			removeMessageFromActive(pendingId);
			insertMessageToActive(responseMessage);
		}
		
		set({ error: '', loading: false });
		
	} catch (err) {
		set({ error: getErrorMessage(err), loading: false });
	}
};

// Helper function to update a message in the active conversation
const updateMessageInActive = (messageId: number, updatedMessage: Message) => {
	const state = store.get();
	const activeConversation = state.conversations.find(
		(c) => c.id === state.activeConversationId
	);
	
	if (activeConversation) {
		const messageIndex = activeConversation.messages.findIndex(
			(m) => m.id === messageId
		);
		
		if (messageIndex !== -1) {
			activeConversation.messages[messageIndex] = updatedMessage;
			
			set({
				conversations: [...state.conversations]
			});
		}
	}
};
