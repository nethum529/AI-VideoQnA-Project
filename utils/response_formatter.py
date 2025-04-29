"""
Response formatter for the Video QnA
Formats AI responses for better display in the terminal
"""

import re
import textwrap

def format_response(response_text, width=80):
    """
    Format an AI response for better display.
    
    Args:
        response_text (str): The AI's response
        width (int): Maximum width for wrapping
        
    Returns:
        str: Formatted response
    """
    # Determine response type based on content
    if "Card" in response_text and ("Question:" in response_text or "Q:" in response_text):
        return format_flashcards(response_text, width)
    elif any(marker in response_text for marker in ["Summary", "Key Points", "Main Points"]):
        return format_summary(response_text, width)
    else:
        return format_general(response_text, width)

def format_flashcards(response_text, width=80):
    """
    Format flashcards for better display.
    
    Args:
        response_text (str): The AI's response
        width (int): Maximum width for wrapping
        
    Returns:
        str: Formatted flashcards
    """
    # Split into individual cards
    cards = re.split(r'Card\s+\d+:', response_text)
    
    # Format each card
    formatted_cards = []
    
    for i, card in enumerate(cards):
        if not card.strip():
            continue
            
        # Add card header
        formatted_card = f"CARD {i}:"
        
        # Extract question and answer
        question_match = re.search(r'Question:\s*(.*?)(?=Answer:|$)', card, re.DOTALL)
        answer_match = re.search(r'Answer:\s*(.*?)(?=\n\n|$)', card, re.DOTALL)
        
        if question_match:
            question = question_match.group(1).strip()
            wrapped_question = textwrap.fill(question, width=width-4)
            formatted_card += f"\n  Q: {wrapped_question}"
        
        if answer_match:
            answer = answer_match.group(1).strip()
            wrapped_answer = textwrap.fill(answer, width=width-4)
            formatted_card += f"\n  A: {wrapped_answer}"
        
        formatted_cards.append(formatted_card)
    
    # Join all cards
    return "\n\n".join(formatted_cards)

def format_summary(response_text, width=80):
    """
    Format summary for better display.
    
    Args:
        response_text (str): The AI's response
        width (int): Maximum width for wrapping
        
    Returns:
        str: Formatted summary
    """
    # Split into paragraphs
    paragraphs = response_text.split('\n\n')
    
    # Format each paragraph
    formatted_paragraphs = []
    
    for paragraph in paragraphs:
        # Check if it's a bullet point list
        if re.match(r'^\s*[-•*]\s', paragraph):
            # Split into bullet points
            bullet_points = re.split(r'\n\s*[-•*]\s', paragraph)
            
            # Format each bullet point
            formatted_bullet_points = []
            
            for i, point in enumerate(bullet_points):
                if i == 0 and not point.strip():
                    continue
                    
                wrapped_point = textwrap.fill(point.strip(), width=width-2, subsequent_indent='  ')
                formatted_bullet_points.append(f"• {wrapped_point}")
            
            formatted_paragraphs.append('\n'.join(formatted_bullet_points))
        else:
            # Regular paragraph
            wrapped_paragraph = textwrap.fill(paragraph.strip(), width=width)
            formatted_paragraphs.append(wrapped_paragraph)
    
    # Join all paragraphs
    return "\n\n".join(formatted_paragraphs)

def format_general(response_text, width=80):
    """
    Format general response for better display.
    
    Args:
        response_text (str): The AI's response
        width (int): Maximum width for wrapping
        
    Returns:
        str: Formatted response
    """
    # Split into paragraphs
    paragraphs = response_text.split('\n\n')
    
    # Format each paragraph
    formatted_paragraphs = []
    
    for paragraph in paragraphs:
        # Check if it's a bullet point list
        if re.match(r'^\s*[-•*]\s', paragraph):
            # Split into bullet points
            bullet_points = re.split(r'\n\s*[-•*]\s', paragraph)
            
            # Format each bullet point
            formatted_bullet_points = []
            
            for i, point in enumerate(bullet_points):
                if i == 0 and not point.strip():
                    continue
                    
                wrapped_point = textwrap.fill(point.strip(), width=width-2, subsequent_indent='  ')
                formatted_bullet_points.append(f"• {wrapped_point}")
            
            formatted_paragraphs.append('\n'.join(formatted_bullet_points))
        else:
            # Regular paragraph
            wrapped_paragraph = textwrap.fill(paragraph.strip(), width=width)
            formatted_paragraphs.append(wrapped_paragraph)
    
    # Join all paragraphs
    return "\n\n".join(formatted_paragraphs)

def main():
    """Test the response formatter"""
    # Test flashcard formatting
    flashcard_response = """Card 1:
Question: What is a vector space?
Answer: A vector space is a set of vectors that can be added together and multiplied by scalars, satisfying certain axioms like associativity, commutativity, and distributivity.

Card 2:
Question: What are the key properties of vector spaces?
Answer: The key properties include closure under addition and scalar multiplication, the existence of a zero vector, and the existence of additive inverses for all vectors."""

    print("\nOriginal Flashcards:")
    print("-" * 80)
    print(flashcard_response)
    print("-" * 80)
    
    print("\nFormatted Flashcards:")
    print("-" * 80)
    print(format_response(flashcard_response))
    print("-" * 80)
    
    # Test summary formatting
    summary_response = """Summary of Vector Spaces:

Vector spaces are fundamental mathematical structures in linear algebra. They consist of vectors that can be added together and multiplied by scalars.

Key properties include:
• Closure under addition and scalar multiplication
• Associativity and commutativity of addition
• Existence of a zero vector
• Existence of additive inverses

Examples of vector spaces include:
• R^n (n-dimensional real coordinate space)
• Polynomial spaces
• Function spaces"""

    print("\nOriginal Summary:")
    print("-" * 80)
    print(summary_response)
    print("-" * 80)
    
    print("\nFormatted Summary:")
    print("-" * 80)
    print(format_response(summary_response))
    print("-" * 80)

if __name__ == "__main__":
    main()