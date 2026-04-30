# Auto-extracted from original RAG/app.py for modular architecture

import re
from langchain_core.messages import HumanMessage

def generate_follow_up_questions(question, answer, small_llm, max_questions=3, chat_history=None):
    """
    Generate follow-up questions based on the user's question and the assistant's answer.
    Questions are designed to continue the conversation context.
    
    Args:
        question: The original user question
        answer: The assistant's answer
        small_llm: LLM instance for generating questions (use small_llm for cost efficiency)
        max_questions: Number of follow-up questions to generate (default: 3)
        chat_history: Previous conversation turns (optional, for context-aware questions)
    
    Returns:
        List of follow-up questions (strings)
    """
    try:
        # Build context section if chat history exists (use all available history)
        context_section = ""
        if chat_history and len(chat_history) > 0:
            # Use all available chat history for better context
            context_section = "\n\nPrevious conversation context:\n" + "\n".join([
                f"User: {turn['user']}\nAssistant: {turn['assistant']}"
                for turn in chat_history
            ]) + "\n"
        
        prompt = f"""Based on the following question and answer{', and the conversation context' if context_section else ''}, generate {max_questions} relevant follow-up questions that would help the user explore the topic further.

Guidelines:
1. Questions should be specific and directly related to the topic discussed
2. Questions should explore different aspects or dive deeper into the answer
3. Questions should be concise and clear (one sentence each)
4. Avoid questions that are too similar to each other
5. Focus on questions that would benefit from the same knowledge base
6. IMPORTANT: All questions must be in English
7. Questions should naturally continue the conversation - they can reference previous context when appropriate
8. Make questions self-contained enough to be understood, but they can build upon previous discussion

{context_section}Current question: {question}

Current answer: {answer[:1000]}  # Limit answer length to avoid token waste

Generate exactly {max_questions} follow-up questions in English, one per line, without numbering or bullets:"""

        response = small_llm.invoke([HumanMessage(content=prompt)])
        
        # Extract questions from response
        if hasattr(response, 'content'):
            questions_text = response.content
        else:
            questions_text = str(response)
        
        # Parse questions (split by newlines, remove empty lines, clean up)
        questions = []
        for line in questions_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Remove numbering/bullets if present (e.g., "1. ", "- ", "• ")
            line = re.sub(r'^[\d\.\-\•\*]\s+', '', line)
            # Remove common prefixes
            line = re.sub(r'^(Question|Q|Follow-up|Followup)[\d\.\:\s\-]*', '', line, flags=re.IGNORECASE)
            line = line.strip()
            
            # Only include substantial questions (at least 10 characters)
            if line and len(line) > 10:
                # Remove trailing punctuation that might be formatting
                line = line.rstrip('.,;:')
                questions.append(line)
        
        # If we got fewer questions than expected, try alternative parsing
        if len(questions) < max_questions:
            # Try splitting by common separators
            alt_questions = re.split(r'[;\n]{2,}|(?<=\?)\s+(?=[A-Z])', questions_text)
            for q in alt_questions:
                q = q.strip()
                if q and len(q) > 10 and q not in questions:
                    q = re.sub(r'^[\d\.\-\•\*]\s+', '', q)
                    q = re.sub(r'^(Question|Q|Follow-up|Followup)[\d\.\:\s\-]*', '', q, flags=re.IGNORECASE)
                    q = q.strip().rstrip('.,;:')
                    if q and len(q) > 10:
                        questions.append(q)
                        if len(questions) >= max_questions:
                            break
        
        # Return up to max_questions
        return questions[:max_questions]
        
    except Exception as e:
        # If generation fails, return empty list
        return []

