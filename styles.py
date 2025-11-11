# styles.py

from themes import THEMES

def load_css(theme_name="Default"):
    """
    Returns a robust CSS that uses a full theme definition for a layered look.
    """
    # Set "Rose Petal" as the new default theme
    theme = THEMES.get(theme_name, THEMES["Rose Petal"]) 
    
    css = f"""
        <style>
            /* --- Main App and Sidebar --- */
            .stApp {{
                background-color: {theme['page_bg']};
            }}
            
            [data-testid="stSidebar"] {{
                background-color: {theme['container_bg']};
            }}

            /* --- The main container for the entire chat page --- */
            .chat-page-container {{
                background: {theme['container_bg']};
                border: 1px solid rgba(0, 0, 0, 0.05);
                border-radius: 15px;
                padding: 1rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                display: flex;
                flex-direction: column;
                height: 85vh;
            }}
            
            /* --- Custom styled header for the chat partner's name --- */
            .chat-header {{
                padding-bottom: 1rem;
                border-bottom: 1px solid rgba(0, 0, 0, 0.08);
                margin-bottom: 1rem;
                font-size: 1.25rem;
                font-weight: 600;
                color: {theme['header_text']};
            }}

            /* --- The scrolling message area --- */
            .chat-container {{
                flex-grow: 1;
                display: flex;
                flex-direction: column-reverse;
                overflow-y: auto;
                margin-bottom: 1rem;
            }}

            /* --- Style for the placeholder message when chat is empty --- */
            .empty-chat-message {{
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100%;
                color: #888;
                font-style: italic;
            }}

            /* --- Message Rows and Bubbles --- */
            .message-row {{
                display: flex;
                width: 100%;
                margin-bottom: 5px;
            }}
            .user-message-row {{ justify-content: flex-end; }}
            .other-message-row {{ justify-content: flex-start; }}

            .chat-message {{
                padding: 10px 15px;
                border-radius: 20px;
                max-width: 80%;
                word-wrap: break-word;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            }}
            
            /* --- Use specific text colors for each bubble type --- */
            .user-message {{ 
                background-color: {theme['sender_bubble_bg']}; 
                color: {theme['sender_bubble_text']};
            }}
            .other-message {{ 
                background-color: {theme['receiver_bubble_bg']}; 
                color: {theme['receiver_bubble_text']};
            }}
            
            .sender {{ 
                font-weight: bold; 
                font-size: 0.9em; 
                margin-bottom: 5px;
            }}
            .timestamp {{ 
                font-size: 0.75em; 
                color: rgba(0, 0, 0, 0.5); /* Semi-transparent black for timestamps */
                align-self: flex-end; 
            }}
        </style>
    """
    return css